# QuickScrub V1

A local, private, and modular PII scrubber with a clean, modern web UI. Built with FastAPI and Vanilla JavaScript.

*No data ever leaves your machine. Scrub with confidence.*

---

<!-- It's highly recommended to replace this with a real screenshot or GIF of the application in action. -->
 

---

## Table of Contents

- [✨ Features](#-features)
- [🛠️ Technology Stack](#️-technology-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Option 1: Running with Docker (Recommended)](#option-1-running-with-docker-recommended)
  - [Option 2: Local Installation](#option-2-local-installation)
- [💻 Usage](#-usage)
  - [Web UI](#web-ui)
  - [API Endpoint](#api-endpoint)
- [🧩 Extending QuickScrub](#-extending-quickscrub)
- [📂 Project Structure](#-project-structure)
- [📜 License](#-license)


## ✨ Features

- **✅ 100% Local & Private:** Runs entirely on your machine. No data is sent to external servers.
- **🎨 Modern Web UI:** A clean, responsive, and easy-to-use interface for scrubbing text.
- **⚙️ Modular Recognizers:** The system automatically discovers new PII recognizers. It's easy to add your own.
- **🛡️ Conflict Resolution:** Intelligently handles overlapping findings (e.g., if one recognizer finds a subset of another).
- **📝 Allow Lists:** Specify values (like `127.0.0.1`) to ignore during the scrubbing process.
- **📦 Containerized:** Includes a multi-stage `Dockerfile` for easy, isolated deployment.
- **🔍 Supported Types (V1):**
  - IP Addresses (v4)
  - Email Addresses
  - Phone Numbers (US-style)
  - Credit Card Numbers (Luhn-validated)
  - MAC Addresses

## 🛠️ Technology Stack

- **Backend:** Python 3.10, FastAPI, Pydantic
- **Frontend:** Vanilla JavaScript (ESM), Vite, HTML5, CSS3
- **Testing:** Pytest
- **Containerization:** Docker

## 🚀 Getting Started

### Prerequisites

- For local installation: Python 3.8+ and Node.js 18+
- For Docker: Docker Engine installed and running.

---

### Option 1: Running with Docker (Recommended)

This is the simplest way to get QuickScrub running without installing Python or Node.js dependencies on your host machine.

1.  **Build the Docker image:**
    From the project root directory, run:
    ```bash
    docker build -t quickscrub .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name quickscrub-app quickscrub
    ```
    - `-d` runs the container in detached mode.
    - `-p 8000:8000` maps port 8000 on your machine to port 8000 in the container.

The application will be available at `http://127.0.0.1:8000`.

---

### Option 2: Local Installation

Follow these steps if you prefer to run the application directly on your machine.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd QuickScrub
    ```

2.  **Set up the Python environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"
    ```
    *Note: The `-e` flag installs the project in "editable" mode.*

3.  **Set up the frontend:**
    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

4.  **Run the application:**
    From the project root directory, run:
    ```bash
    uvicorn QuickScrub.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## 💻 Usage

### Web UI

1.  Navigate to `http://127.0.0.1:8000` in your browser.
2.  Paste the text you want to analyze into the **Input Text** box.
3.  Select the PII types you wish to find and scrub.
4.  Optionally, add any values to the **Allow List** to prevent them from being scrubbed (one value per line).
5.  Click **Scrub Text** or press `Ctrl+Enter`.
6.  The scrubbed text and a corresponding legend will appear on the right.

### API Endpoint

You can also use the backend API directly.

**`POST /api/scrub`**

-   **Content-Type:** `application/json`
-   **Request Body:**
    ```json
    {
      "text": "string",
      "types": ["list", "of", "strings"],
      "allow_list": ["optional", "list"]
    }
    ```
-   **Example using `curl`:**
    ```bash
    curl -X POST http://127.0.0.1:8000/api/scrub \
    -H "Content-Type: application/json" \
    -d '{
      "text": "My email is user@example.com and my IP is 192.168.1.1, but ignore 127.0.0.1.",
      "types": ["EMAIL", "IP_ADDRESS"],
      "allow_list": ["127.0.0.1"]
    }'
    ```

## 🧩 Extending QuickScrub

Adding a new PII recognizer is simple thanks to the modular design.

1.  Create a new Python file in `QuickScrub/recognizers/` (e.g., `my_recognizer.py`).
2.  In that file, create a class that inherits from `Recognizer` (from `QuickScrub.recognizers.base`).
3.  In your class `__init__`, call `super().__init__(name="My Recognizer Name", tag="MY_TAG")`. The `tag` must be unique.
4.  Implement the `analyze(self, text: str) -> List[Finding]` method. This method should scan the text and return a list of `Finding` objects for each match.
5.  That's it! The application will automatically discover and load your new recognizer on startup.

## 📂 Project Structure

```
QuickScrub/
├── Dockerfile              # For building the production Docker image.
├── frontend/               # All frontend Vanilla JS source code.
│   ├── src/
│   ├── index.html
│   └── vite.config.js
├── QuickScrub/             # The main Python package for the backend.
│   ├── __init__.py
│   ├── main.py             # FastAPI app entrypoint, middleware, static files.
│   ├── api/                # API endpoints.
│   ├── core/               # Core logic (engine, recognizer registry).
│   ├── models/             # Pydantic and Dataclass models.
│   ├── recognizers/        # All PII recognizer plugins.
│   │   ├── base.py         # Abstract base classes.
│   │   └── ...             # Individual recognizer implementations.
│   └── tests/              # Pytest unit tests.
├── pyproject.toml          # Project metadata and dependencies.
└── README.md               # You are here!
```

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.
