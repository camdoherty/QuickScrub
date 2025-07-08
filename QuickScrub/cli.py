# FILE: QuickScrub/cli.py

import sys
import typer
import json
from typing import List, Optional
from pathlib import Path

# Import the core components from our existing application
from .core.engine import ScrubberEngine
from .core.registry import RecognizerRegistry
from .models.data_models import ScrubTask

# Create a single Typer application instance
app = typer.Typer(
    name="quickscrub",
    help="A local, private PII scrubber that runs from your terminal."
)

# Instantiate the engine and registry once to be reused by commands
ENGINE_INSTANCE = ScrubberEngine()
REGISTRY_INSTANCE = RecognizerRegistry()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    text: Optional[str] = typer.Argument(
        None,
        help="The text to scrub. If not provided, reads from standard input (stdin)."
    ),
    types: Optional[List[str]] = typer.Option(
        None, "--type", "-t",
        help="Specify a PII type to scrub. Can be used multiple times. (Default: all types)"
    ),
    allow_list_file: Optional[Path] = typer.Option(
        None, "--allow-list", "-a",
        help="Path to a file containing values to ignore, one per line."
    ),
    as_json: bool = typer.Option(
        False, "--json",
        help="Output the result as a JSON object with scrubbed text and legend."
    )
):
    """
    Scrub text to find and replace PII.
    
    Accepts text directly as an argument or piped from stdin, e.g.:
    cat report.log | quickscrub --type EMAIL
    """
    # If a subcommand is invoked, we don't want to run the scrub logic.
    if ctx.invoked_subcommand is not None:
        return

    input_text = text
    # If no direct text argument, check for piped input from stdin
    if input_text is None:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            # If no command is specified and no text is provided, show help.
            typer.echo(ctx.get_help())
            raise typer.Exit()

    # If no types are specified, use all available recognizers
    scrub_types = types if types else list(REGISTRY_INSTANCE.recognizers.keys())
    
    # Load allow list from file if provided
    allow_list = []
    if allow_list_file:
        if allow_list_file.is_file():
            allow_list = [line.strip() for line in allow_list_file.read_text().splitlines() if line.strip()]
        else:
            typer.echo(f"Error: Allow list file not found at '{allow_list_file}'", err=True)
            raise typer.Exit(code=1)

    # Perform the scrub operation
    task = ScrubTask(text=input_text, types=scrub_types, allow_list=allow_list)
    all_findings = REGISTRY_INSTANCE.get_findings(task.text, task.types)
    result = ENGINE_INSTANCE.scrub(task, all_findings)

    # Output the result
    if as_json:
        output = {
            "scrubbed_text": result.scrubbed_text,
            "legend": result.legend
        }
        typer.echo(json.dumps(output, indent=2))
    else:
        typer.echo(result.scrubbed_text)


@app.command()
def types():
    """
    List all available PII recognizer types.
    """
    typer.echo("Available PII Recognizer Types:")
    for tag in sorted(REGISTRY_INSTANCE.recognizers.keys()):
        typer.echo(f"- {tag}")


if __name__ == "__main__":
    app()
