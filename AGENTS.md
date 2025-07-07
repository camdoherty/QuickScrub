### **Instructions for Codex/ChatGPT**

**Objective:** Implement the QuickScrub V1 application from scratch.

**Instructions:**
1.  You are working in an empty git repository (the git repo has been cleared for a fresh start). Your first task is to create the entire directory and file structure for the project.
2.  After creating the structure, populate each file with the exact content provided in the steps below.
3.  Follow the steps sequentially. Create all specified files.
4.  Do not add any files or logic not specified in these instructions.

Proceed.

---

### **Part 1: Project Initialization**

**Action:** Create the necessary directories and empty Python `__init__.py` files.

Execute the following commands from the project root:

```bash
# Create main directories
mkdir -p QuickScrub/api QuickScrub/core QuickScrub/models QuickScrub/recognizers QuickScrub/tests
mkdir -p frontend/src

# Create empty Python package initializer files
touch QuickScrub/__init__.py
touch QuickScrub/api/__init__.py
touch QuickScrub/core/__init__.py
touch QuickScrub/models/__init__.py
touch QuickScrub/recognizers/__init__.py
touch QuickScrub/tests/__init__.py
```

### **Part 2: Backend Implementation**

**Step 2.1: Define Project Dependencies**
*   **Action:** Create the file `pyproject.toml`.
*   **File Path:** `pyproject.toml`
*   **Content:**
    ```toml
    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "QuickScrub"
    version = "1.0.0"
    description = "A local, modular PII scrubber with a web UI."
    readme = "README.md"
    requires-python = ">=3.8"
    dependencies = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0",
        "pydantic>=2.0",
        "python-multipart>=0.0.9"
    ]

    [project.optional-dependencies]
    dev = [
        "pytest",
        "requests",
    ]
    ```

**Step 2.2: Define Recognizer Base Contracts**
*   **Action:** Create the file `QuickScrub/recognizers/base.py`.
*   **File Path:** `QuickScrub/recognizers/base.py`
*   **Content:**
    ```python
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    from typing import List

    @dataclass(frozen=True, order=True)
    class Finding:
        """
        An immutable data object representing a single piece of PII found in text.
        'order=True' automatically makes this class comparable, first by 'start'
        index, then by 'end' index, critical for conflict resolution.
        """
        start: int
        end: int
        value: str
        type: str
        recognizer_name: str

    class Recognizer(ABC):
        """The abstract base class for all PII recognizer plugins."""
        def __init__(self, name: str, tag: str):
            if not name or not tag:
                raise ValueError("Recognizer name and tag cannot be empty.")
            self.name = name
            self.tag = tag

        @abstractmethod
        def analyze(self, text: str) -> List[Finding]:
            """Scans the input text and returns a list of all findings."""
            pass

        def __repr__(self) -> str:
            return f"<{self.__class__.__name__}(name='{self.name}', tag='{self.tag}')>"
    ```

**Step 2.3: Define Application Data Models**
*   **Action:** Create the file `QuickScrub/models/data_models.py`.
*   **File Path:** `QuickScrub/models/data_models.py`
*   **Content:**
    ```python
    from dataclasses import dataclass, field
    from typing import List, Dict, Optional
    from pydantic import BaseModel, Field

    class ScrubRequest(BaseModel):
        """The request model for the /api/scrub endpoint."""
        text: str = Field(..., description="The input text to be scrubbed.")
        types: List[str] = Field(..., description="A list of PII type tags to scrub (e.g., ['IP_ADDRESS', 'EMAIL']).")
        allow_list: Optional[List[str]] = Field(default_factory=list, description="A list of values to ignore during scrubbing.")

    class LegendItem(BaseModel):
        """Represents a single entry in the response legend."""
        original: str
        mock: str
        type: str

    class ScrubResponse(BaseModel):
        """The response model for the /api/scrub endpoint."""
        scrubbed_text: str
        legend: List[LegendItem]

    @dataclass(frozen=True)
    class ScrubTask:
        """Internal data structure for passing a scrub job to the Core Engine."""
        text: str
        types: List[str]
        allow_list: List[str] = field(default_factory=list)

    @dataclass(frozen=True)
    class ScrubResult:
        """Internal data structure for returning a result from the Core Engine."""
        scrubbed_text: str
        legend: List[Dict[str, str]]
    ```

**Step 2.4: Implement the Core Scrubber Engine**
*   **Action:** Create the file `QuickScrub/core/engine.py`.
*   **File Path:** `QuickScrub/core/engine.py`
*   **Content:**
    ```python
    from typing import List, Dict
    from ..models.data_models import ScrubTask, ScrubResult
    from ..recognizers.base import Finding

    class ScrubberEngine:
        def scrub(self, task: ScrubTask, findings: List[Finding]) -> ScrubResult:
            final_findings = self._resolve_conflicts(findings, task.allow_list)
            scrubbed_text, legend = self._scrub_text(task.text, final_findings)
            return ScrubResult(scrubbed_text=scrubbed_text, legend=legend)

        def _resolve_conflicts(self, findings: List[Finding], allow_list: List[str]) -> List[Finding]:
            allow_set = {item.lower() for item in allow_list}
            allowed_findings = [f for f in findings if f.value.lower() not in allow_set]
            sorted_findings = sorted(allowed_findings, key=lambda f: (f.start, -f.end))

            resolved: List[Finding] = []
            if not sorted_findings: return resolved

            last_accepted_finding = sorted_findings[0]
            resolved.append(last_accepted_finding)

            for current_finding in sorted_findings[1:]:
                if current_finding.start < last_accepted_finding.end: continue
                resolved.append(current_finding)
                last_accepted_finding = current_finding
            
            return resolved

        def _scrub_text(self, text: str, findings: List[Finding]) -> (str, List[Dict[str, str]]):
            scrubbed_text = text
            legend: List[Dict[str, str]] = []
            placeholder_counts: Dict[str, int] = {}

            for finding in reversed(findings):
                pii_type = finding.type
                count = placeholder_counts.get(pii_type, 0) + 1
                placeholder_counts[pii_type] = count
                placeholder = f"[{pii_type}_{count}]"
                scrubbed_text = scrubbed_text[:finding.start] + placeholder + scrubbed_text[finding.end:]
                legend.insert(0, {"original": finding.value, "mock": placeholder, "type": pii_type})

            return scrubbed_text, legend
    ```

**Step 2.5: Implement the Recognizer Registry**
*   **Action:** Create the file `QuickScrub/core/registry.py`.
*   **File Path:** `QuickScrub/core/registry.py`
*   **Content:**
    ```python
    import pkgutil
    import inspect
    import logging
    from typing import List, Dict
    from ..recognizers.base import Recognizer, Finding
    from .. import recognizers as recognizers_package

    class RecognizerRegistry:
        def __init__(self):
            self.recognizers: Dict[str, Recognizer] = {}
            self._discover_recognizers()

        def _discover_recognizers(self):
            for _, name, _ in pkgutil.iter_modules(recognizers_package.__path__):
                try:
                    module = __import__(f"{recognizers_package.__name__}.{name}", fromlist=[""])
                    for _, cls in inspect.getmembers(module, inspect.isclass):
                        if issubclass(cls, Recognizer) and cls is not Recognizer:
                            instance = cls()
                            if instance.tag in self.recognizers:
                                logging.warning(f"Duplicate recognizer tag '{instance.tag}' found. Overwriting.")
                            self.recognizers[instance.tag] = instance
                except Exception as e:
                    logging.error(f"Failed to load recognizer module {name}: {e}", exc_info=True)
            logging.info(f"Discovered recognizers: {list(self.recognizers.keys())}")

        def get_findings(self, text: str, requested_types: List[str]) -> List[Finding]:
            all_findings = []
            for pii_type in requested_types:
                if recognizer := self.recognizers.get(pii_type):
                    try:
                        findings = recognizer.analyze(text)
                        all_findings.extend(findings)
                    except Exception as e:
                        logging.error(f"Error running recognizer '{recognizer.name}': {e}", exc_info=True)
            return all_findings
    ```

**Step 2.6: Implement Recognizers**
*   **Action:** Create the following five recognizer files.
*   **File 1:** `QuickScrub/recognizers/ip_recognizer.py`
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class IpRecognizer(Recognizer):
        IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        def __init__(self): super().__init__(name="IP Address", tag="IP_ADDRESS")
        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.IP_REGEX.finditer(text):
                ip = match.group(0)
                if all(0 <= int(octet) <= 255 for octet in ip.split('.')):
                    findings.append(Finding(match.start(), match.end(), ip, self.tag, self.name))
            return findings
    ```
*   **File 2:** `QuickScrub/recognizers/email_recognizer.py`
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class EmailRecognizer(Recognizer):
        EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        def __init__(self): super().__init__(name="Email Address", tag="EMAIL")
        def analyze(self, text: str) -> List[Finding]:
            return [Finding(m.start(), m.end(), m.group(0), self.tag, self.name) for m in self.EMAIL_REGEX.finditer(text)]
    ```
*   **File 3:** `QuickScrub/recognizers/mac_recognizer.py`
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class MacAddressRecognizer(Recognizer):
        MAC_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b|\b(?:[0-9A-Fa-f]{4}\.){2}(?:[0-9A-Fa-f]{4})\b')
        def __init__(self): super().__init__(name="MAC Address", tag="MAC_ADDRESS")
        def analyze(self, text: str) -> List[Finding]:
            return [Finding(m.start(), m.end(), m.group(0), self.tag, self.name) for m in self.MAC_REGEX.finditer(text)]
    ```
*   **File 4:** `QuickScrub/recognizers/phone_recognizer.py`
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class PhoneRecognizer(Recognizer):
        PHONE_REGEX = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        def __init__(self): super().__init__(name="Phone Number", tag="PHONE")
        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.PHONE_REGEX.finditer(text):
                if len(re.sub(r'\D', '', match.group(0))) >= 10:
                    findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            return findings
    ```
*   **File 5:** `QuickScrub/recognizers/credit_card_recognizer.py`
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class CreditCardRecognizer(Recognizer):
        CC_REGEX = re.compile(r'\b(?:\d[ -]?){12,18}\d\b')
        def __init__(self): super().__init__(name="Credit Card", tag="CREDIT_CARD")
        def _is_luhn_valid(self, n: str) -> bool:
            try:
                d = [int(x) for x in reversed(n)]; c = sum(d[::2]) + sum(sum(divmod(i * 2, 10)) for i in d[1::2])
                return c % 10 == 0
            except (ValueError, TypeError): return False
        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.CC_REGEX.finditer(text):
                cc_digits = re.sub(r'\D', '', match.group(0))
                if 13 <= len(cc_digits) <= 19 and self._is_luhn_valid(cc_digits):
                    findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            return findings
    ```

**Step 2.7: Implement API Endpoints**
*   **Action:** Create the file `QuickScrub/api/endpoints.py`.
*   **File Path:** `QuickScrub/api/endpoints.py`
*   **Content:**
    ```python
    from fastapi import APIRouter, Depends
    from ..models.data_models import ScrubRequest, ScrubResponse, LegendItem, ScrubTask
    from ..core.engine import ScrubberEngine
    from ..core.registry import RecognizerRegistry

    router = APIRouter()

    # --- Singleton Instances ---
    ENGINE_INSTANCE = ScrubberEngine()
    REGISTRY_INSTANCE = RecognizerRegistry()

    # --- Dependency Injection Functions ---
    def get_engine() -> ScrubberEngine: return ENGINE_INSTANCE
    def get_registry() -> RecognizerRegistry: return REGISTRY_INSTANCE

    # --- API Endpoint ---
    @router.post("/scrub", response_model=ScrubResponse)
    async def scrub_text(
        request: ScrubRequest,
        engine: ScrubberEngine = Depends(get_engine),
        registry: RecognizerRegistry = Depends(get_registry)
    ):
        task = ScrubTask(text=request.text, types=request.types, allow_list=request.allow_list or [])
        all_findings = registry.get_findings(task.text, task.types)
        result = engine.scrub(task, all_findings)
        return ScrubResponse(
            scrubbed_text=result.scrubbed_text,
            legend=[LegendItem(**item) for item in result.legend]
        )
    ```

**Step 2.8: Create Main Application Entrypoint**
*   **Action:** Create the file `QuickScrub/main.py`.
*   **File Path:** `QuickScrub/main.py`
*   **Content:**
    ```python
    import logging
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from .api import endpoints

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = FastAPI(title="QuickScrub API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logging.error(f"Unhandled exception for {request.url}: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})

    app.include_router(endpoints.router, prefix="/api")

    try:
        app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
    except RuntimeError:
        logging.warning("Frontend 'dist' directory not found. Run 'npm install && npm run build' in 'frontend'.")
    ```

### **Part 3: Testing Implementation**

**Step 3.1: Write Tests for the Core Engine**
*   **Action:** Create the file `QuickScrub/tests/test_engine.py`.
*   **File Path:** `QuickScrub/tests/test_engine.py`
*   **Content:**
    ```python
    import unittest
    from ..core.engine import ScrubberEngine
    from ..recognizers.base import Finding
    from ..models.data_models import ScrubTask

    class TestScrubberEngine(unittest.TestCase):
        def setUp(self): self.engine = ScrubberEngine()
        def test_resolve_no_overlap(self):
            findings = [Finding(0,3,"f","T1","R1"), Finding(4,7,"b","T2","R2")]; r = self.engine._resolve_conflicts(findings, []); self.assertEqual(len(r), 2)
        def test_resolve_with_allow_list(self):
            findings = [Finding(0,3,"foo","T1","R1"), Finding(4,7,"bar","T2","R2")]; r = self.engine._resolve_conflicts(findings, ["bar"]); self.assertEqual(len(r), 1); self.assertEqual(r[0].value, "foo")
        def test_resolve_complete_overlap(self):
            findings = [Finding(5,21,"long","T_L","R_L"), Finding(9,17,"short","T_S","R_S")]; r = self.engine._resolve_conflicts(findings, []); self.assertEqual(len(r), 1); self.assertEqual(r[0].type, "T_L")
        def test_full_scrub_process(self):
            text = "IP 1.1.1.1 and email test@dev.com."; findings = [Finding(3,10,"1.1.1.1","IP","IP"), Finding(21,35,"test@dev.com","EMAIL","Email")]
            task = ScrubTask(text=text, types=["IP", "EMAIL"]); result = self.engine.scrub(task, findings)
            self.assertEqual(result.scrubbed_text, "IP [IP_1] and email [EMAIL_1]."); self.assertEqual(len(result.legend), 2)
    ```

**Step 3.2: Write Tests for Recognizers**
*   **Action:** Create the file `QuickScrub/tests/test_recognizers.py`.
*   **File Path:** `QuickScrub/tests/test_recognizers.py`
*   **Content:**
    ```python
    import unittest
    from ..recognizers.ip_recognizer import IpRecognizer
    from ..recognizers.email_recognizer import EmailRecognizer
    from ..recognizers.credit_card_recognizer import CreditCardRecognizer

    class TestRecognizers(unittest.TestCase):
        def test_ip_recognizer(self):
            r = IpRecognizer(); f = r.analyze("IPs: 192.168.1.1 and 300.0.0.1"); self.assertEqual(len(f), 1); self.assertEqual(f[0].value, "192.168.1.1")
        def test_email_recognizer(self):
            r = EmailRecognizer(); f = r.analyze("Contact test@example.com."); self.assertEqual(len(f), 1)
        def test_credit_card_recognizer(self):
            r = CreditCardRecognizer(); self.assertEqual(len(r.analyze("Card: 499273987169822")), 1); self.assertEqual(len(r.analyze("Card: 1234567812345678")), 0)
    ```

### **Part 4: Frontend Implementation**

**Step 4.1: Create Frontend Dependencies**
*   **Action:** Create the file `frontend/package.json`.
*   **File Path:** `frontend/package.json`
*   **Content:**
    ```json
    {
      "name": "quickscrub-frontend",
      "private": true,
      "version": "1.0.0",
      "type": "module",
      "scripts": {
        "dev": "vite",
        "build": "vite build",
        "preview": "vite preview"
      },
      "devDependencies": {
        "vite": "^4.4.5"
      }
    }
    ```

**Step 4.2: Configure Vite**
*   **Action:** Create the file `frontend/vite.config.js`.
*   **File Path:** `frontend/vite.config.js`
*   **Content:**
    ```javascript
    import { defineConfig } from 'vite'

    export default defineConfig({
      server: {
        proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
      },
      build: { outDir: 'dist' },
    })
    ```

**Step 4.3: Create HTML Structure**
*   **Action:** Create the file `frontend/index.html`.
*   **File Path:** `frontend/index.html`
*   **Content:**
    ```html
    <!doctype html>
    <html lang="en">
      <head><meta charset="UTF-8" /><title>QuickScrub V1</title></head>
      <body>
        <div id="app">
          <header><h1>QuickScrub V1</h1></header>
          <main>
            <div class="container">
              <div class="input-section">
                <h2>Input Text</h2>
                <textarea id="inputText" placeholder="Paste your text here..."></textarea>
                <h2>PII Types to Scrub</h2>
                <div id="pii-types-checkboxes" class="checkbox-grid"></div>
                <h2>Allow List (optional, one per line)</h2>
                <textarea id="allowList" placeholder="127.0.0.1..."></textarea>
                <button id="scrubButton">Scrub Text</button>
              </div>
              <div class="output-section">
                <h2>Scrubbed Text</h2>
                <div class="output-box-container">
                    <pre id="scrubbedText" class="output-box"></pre>
                    <button class="copy-button" id="copyScrubbedText">Copy</button>
                </div>
                <h2>Legend</h2>
                <div class="output-box-container">
                    <div id="legend" class="output-box"></div>
                    <button class="copy-button" id="copyLegend">Copy</button>
                </div>
              </div>
            </div>
          </main>
        </div>
        <script type="module" src="/src/main.js"></script>
      </body>
    </html>
    ```

**Step 4.4: Create CSS Styles**
*   **Action:** Create the file `frontend/src/style.css`.
*   **File Path:** `frontend/src/style.css`
*   **Content:**
    ```css
    :root { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; font-weight: 400; color-scheme: light dark; color: rgba(255, 255, 255, 0.87); background-color: #242424; }
    body { margin: 0; display: flex; place-items: center; min-height: 100vh; }
    #app { max-width: 1280px; margin: 0 auto; padding: 2rem; text-align: center; }
    .container { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; text-align: left; }
    h2 { margin-top: 1.5rem; margin-bottom: 0.5rem; border-bottom: 1px solid #555; padding-bottom: 0.25rem; }
    textarea { width: 100%; min-height: 200px; padding: 0.5rem; border-radius: 4px; border: 1px solid #555; background-color: #333; color: #eee; resize: vertical; }
    #allowList { min-height: 80px; }
    .checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.5rem; }
    #scrubButton { margin-top: 1rem; padding: 0.6em 1.2em; font-size: 1em; cursor: pointer; border-radius: 8px; border: 1px solid transparent; background-color: #1a1a1a; transition: border-color 0.25s; }
    #scrubButton:hover { border-color: #646cff; }
    #scrubButton:disabled { cursor: not-allowed; opacity: 0.5; }
    .output-box-container { position: relative; }
    .output-box { background-color: #1a1a1a; padding: 1rem; border-radius: 4px; min-height: 100px; white-space: pre-wrap; word-wrap: break-word; }
    #legend { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: 0.5rem; padding: 1rem; }
    #legend > .header { font-weight: bold; color: #999; }
    .copy-button { position: absolute; top: 5px; right: 5px; padding: 0.2rem 0.5rem; font-size: 0.8rem; background-color: #333; border: 1px solid #555; border-radius: 4px; cursor: pointer; }
    ```

**Step 4.5: Create JavaScript Logic**
*   **Action:** Create the file `frontend/src/main.js`.
*   **File Path:** `frontend/src/main.js`
*   **Content:**
    ```javascript
    import './style.css'

    const PII_TYPES = [
      { tag: 'IP_ADDRESS', label: 'IP Address' }, { tag: 'EMAIL', label: 'Email' },
      { tag: 'PHONE', label: 'Phone Number' }, { tag: 'CREDIT_CARD', label: 'Credit Card' },
      { tag: 'MAC_ADDRESS', label: 'MAC Address' },
    ];

    document.addEventListener('DOMContentLoaded', () => {
      const chkContainer = document.getElementById('pii-types-checkboxes');
      PII_TYPES.forEach(t => {
        const div = document.createElement('div');
        div.innerHTML = `<input type="checkbox" id="${t.tag}" value="${t.tag}" checked><label for="${t.tag}">${t.label}</label>`;
        chkContainer.appendChild(div);
      });
      document.getElementById('scrubButton').addEventListener('click', handleScrub);
      document.getElementById('copyScrubbedText').addEventListener('click', () => copyToClipboard('scrubbedText'));
      document.getElementById('copyLegend').addEventListener('click', () => copyToClipboard('legend'));
    });

    async function handleScrub() {
      const btn = document.getElementById('scrubButton'), textEl = document.getElementById('scrubbedText'), legendEl = document.getElementById('legend');
      const selectedTypes = PII_TYPES.filter(t => document.getElementById(t.tag).checked).map(t => t.tag);
      if (!document.getElementById('inputText').value || selectedTypes.length === 0) return alert('Input text and at least one PII type are required.');
      
      btn.disabled = true; btn.textContent = 'Scrubbing...';
      textEl.textContent = ''; legendEl.innerHTML = '';

      try {
        const res = await fetch('/api/scrub', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: document.getElementById('inputText').value, types: selectedTypes,
            allow_list: document.getElementById('allowList').value.split('\n').filter(l => l.trim() !== ''),
          }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || `HTTP error! status: ${res.status}`);
        const data = await res.json();
        textEl.textContent = data.scrubbed_text; renderLegend(data.legend);
      } catch (error) {
        alert(`An error occurred: ${error.message}`);
        textEl.textContent = 'An error occurred. Check console for details.';
      } finally {
        btn.disabled = false; btn.textContent = 'Scrub Text';
      }
    }

    function renderLegend(legendData) {
      const el = document.getElementById('legend'); el.innerHTML = '';
      if (legendData.length === 0) { el.textContent = 'No PII was found or scrubbed.'; return; }
      const headers = ['Type', 'Mock', 'Original'];
      headers.forEach(h => { const d = document.createElement('div'); d.className = 'header'; d.textContent = h; el.appendChild(d); });
      legendData.forEach(i => {['type', 'mock', 'original'].forEach(k => { const d = document.createElement('div'); d.textContent = i[k]; el.appendChild(d); }); });
    }

    function copyToClipboard(id) { navigator.clipboard?.writeText(document.getElementById(id).innerText).then(() => alert('Copied!')); }
    ```

### **Part 5: Final Project Files**

**Step 5.1: Create Dockerfile**
*   **Action:** Create the file `Dockerfile`.
*   **File Path:** `Dockerfile`
*   **Content:**
    ```dockerfile
    # Stage 1: Build the frontend
    FROM node:18-alpine AS frontend-builder
    WORKDIR /app/frontend
    COPY frontend/package*.json ./
    RUN npm install
    COPY frontend/ ./
    RUN npm run build

    # Stage 2: Build the backend
    FROM python:3.10-slim AS backend-builder
    WORKDIR /app
    RUN pip install --no-cache-dir --upgrade pip
    COPY pyproject.toml ./
    RUN pip install --no-cache-dir --prefix="/install" .
    COPY QuickScrub ./QuickScrub

    # Stage 3: Final image
    FROM python:3.10-slim
    WORKDIR /app
    COPY --from=backend-builder /install /usr/local
    COPY --from=backend-builder /app/QuickScrub ./QuickScrub
    COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
    
    EXPOSE 8000
    CMD ["uvicorn", "QuickScrub.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

**Step 5.2: Create README**
*   **Action:** Create the file `README.md`.
*   **File Path:** `README.md`
*   **Content:**
    ```markdown
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
    ```

---

**END OF AGENTS.md**