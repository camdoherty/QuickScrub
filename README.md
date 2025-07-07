# QuickScrub V1

A local, private, and modular PII scrubber with a web UI, built with FastAPI and Vanilla JavaScript.

## Features

- **Local & Private:** Runs entirely on your machine. No data is sent to external servers.
- **Modular Recognizers:** Easily add new PII types to detect.
- **Web UI:** Simple interface for scrubbing text and viewing results.
- **Supported Types (V1):** IP Addresses, Emails, Phone Numbers, Credit Cards (Luhn-validated), MAC Addresses.
- **Allow Lists:** Specify values to ignore during scrubbing.

## How to Run

### Prerequisites

- Python 3.8+
- Node.js 18+ and npm

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd QuickScrub
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -e ".[dev]"
    ```

4.  **Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    ```

5.  **Build the static frontend:**
    ```bash
    npm run build
    ```

6.  **Return to the project root:**
    ```bash
    cd ..
    ```

### Running the Application

Execute the following command from the project root directory:

```bash
uvicorn QuickScrub.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.
