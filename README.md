# QuickScrub

A fast, private, local PII (Personally Identifiable Information) scrubber with a modular backend API and a simple web UI.

QuickScrub is designed for developers, analysts, and anyone who needs to quickly and reliably remove sensitive data from blocks of text before sharing, logging, or storing it. Because it runs entirely on your local machine, your data never leaves your computer.

### Key Features

* **Private & Local-First:** All processing happens on your machine. No data is ever sent to a third-party service.
* **Modular Recognizer System:** Easily extend the application by adding new recognizers for different types of PII.
* **Comprehensive V1 Scrubber:** Detects common PII types out-of-the-box:
  * IP Addresses (IPv4)
  * Email Addresses
  * Phone Numbers
  * Credit Card Numbers (with Luhn algorithm validation)
  * MAC Addresses
* **Intelligent Conflict Resolution:** If multiple PII types overlap (e.g., a long number inside a credit card), the engine intelligently picks the most likely (longest) match.
* **Allow Lists:** Specify a list of values (e.g., `127.0.0.1`) that should be ignored by the scrubber.
* **Simple Web UI:** An easy-to-use interface for pasting text, selecting PII types, and viewing the scrubbed results and legend.

### Screenshot

![QuickScrub Screenshot](./docs/screenshot.png)

*(Note: You will need to create this screenshot and place it in a `docs` folder for it to display correctly.)*

---

### Technology Stack

| Backend                               | Frontend                             |
| ------------------------------------- | ------------------------------------ |
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white) |
| **Uvicorn** (ASGI Server)             | **HTML5 & CSS3**                     |

---

## Installation & Setup

Follow these steps to set up your local development environment.

### Prerequisites

* Python 3.8+
* Node.js and npm (or a compatible package manager)

### 1. Clone the Repository

```sh
git clone https://github.com/your-username/QuickScrub.git
cd QuickScrub
```

### 2. Set Up the Python Backend

From the project root directory:

```sh
# Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the project and its dependencies in editable mode
# The [dev] part includes testing libraries like pytest.
pip install -e .[dev]
```

### 3. Set Up the JavaScript Frontend

Navigate to the `frontend` directory and install the required npm packages.

```sh
cd frontend
npm install
```

---

## Usage

To run the application, you need to first build the static frontend files and then run the backend server.

### 1. Build the Frontend

From the `frontend` directory, run the build command. This will compile the UI into a `dist` folder that our backend can serve.

```sh
# Make sure you are in the 'frontend' directory
npm run build
```

### 2. Run the Backend Server

Navigate back to the project root and start the Uvicorn server.

```sh
# Navigate back to the project root
cd ..

# Start the server with hot-reloading
uvicorn QuickScrub.main:app --reload
```

### 3. Access the Application

Once the server is running, open your web browser and navigate to:

**`http://127.0.0.1:8000`**

You should see the QuickScrub web interface. The backend API's interactive documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

---

## Running Tests

To ensure the backend logic is working correctly, you can run the test suite using `pytest`.

```sh
# From the project root directory
pytest
```

---

## API Details

The application exposes a single primary endpoint for developers who wish to use the service programmatically.

### `POST /api/scrub`

Scrubs the provided text for the requested PII types.

**Request Body:**

```json
{
  "text": "The server IP is 192.168.1.1 and my email is test@example.com",
  "types": ["IP_ADDRESS", "EMAIL"],
  "allow_list": ["ignore@this.com"]
}
```

**Success Response (200 OK):**

```json
{
  "scrubbed_text": "The server IP is [IP_ADDRESS_1] and my email is [EMAIL_1]",
  "legend": [
    {
      "original": "192.168.1.1",
      "mock": "[IP_ADDRESS_1]",
      "type": "IP_ADDRESS"
    },
    {
      "original": "test@example.com",
      "mock": "[EMAIL_1]",
      "type": "EMAIL"
    }
  ]
}
```

---

## Architectural Overview

The application is built with a clean, decoupled architecture:

1. **UI Layer (Frontend):** A static single-page application built with Vanilla JS and Vite. It is responsible for all presentation logic.
2. **API Layer (Backend):** A FastAPI application that validates requests, handles HTTP communication, and serves the frontend.
3. **Core Engine:** The framework-agnostic "brain" of the application. It contains the conflict resolution and text scrubbing logic.
4. **Recognizer Subsystem:** A modular "plugin" system where each PII type is handled by its own self-contained `Recognizer` class, making the system easy to extend.

---

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
