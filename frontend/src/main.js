import '../style.css'

const PII_TYPES = [
  { tag: 'IP_ADDRESS', label: 'IP Address' },
  { tag: 'EMAIL', label: 'Email' },
  { tag: 'PHONE', label: 'Phone Number' },
  { tag: 'CREDIT_CARD', label: 'Credit Card' },
  { tag: 'MAC_ADDRESS', label: 'MAC Address' },
];

document.addEventListener('DOMContentLoaded', () => {
  const checkboxesContainer = document.getElementById('pii-types-checkboxes');
  PII_TYPES.forEach(type => {
    const div = document.createElement('div');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = type.tag;
    checkbox.value = type.tag;
    checkbox.checked = true; // Default to checked

    const label = document.createElement('label');
    label.htmlFor = type.tag;
    label.textContent = type.label;

    div.appendChild(checkbox);
    div.appendChild(label);
    checkboxesContainer.appendChild(div);
  });

  const scrubButton = document.getElementById('scrubButton');
  scrubButton.addEventListener('click', handleScrub);

  document.getElementById('copyScrubbedText').addEventListener('click', () => copyToClipboard('scrubbedText'));
  document.getElementById('copyLegend').addEventListener('click', () => copyToClipboard('legend'));
});

async function handleScrub() {
  const scrubButton = document.getElementById('scrubButton');
  const inputText = document.getElementById('inputText').value;
  const allowListText = document.getElementById('allowList').value;
  const scrubbedTextEl = document.getElementById('scrubbedText');
  const legendEl = document.getElementById('legend');

  const selectedTypes = PII_TYPES
    .filter(type => document.getElementById(type.tag).checked)
    .map(type => type.tag);

  if (!inputText || selectedTypes.length === 0) {
    alert('Please provide input text and select at least one PII type.');
    return;
  }

  scrubButton.disabled = true;
  scrubButton.textContent = 'Scrubbing...';
  scrubbedTextEl.textContent = '';
  legendEl.innerHTML = '';

  const body = {
    text: inputText,
    types: selectedTypes,
    allow_list: allowListText.split('\n').filter(line => line.trim() !== ''),
  };

  try {
    const response = await fetch('/api/scrub', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    scrubbedTextEl.textContent = data.scrubbed_text;
    renderLegend(data.legend);

  } catch (error) {
    console.error('Scrubbing failed:', error);
    alert(`An error occurred: ${error.message}`);
    scrubbedTextEl.textContent = 'An error occurred. Check the console for details.';
  } finally {
    scrubButton.disabled = false;
    scrubButton.textContent = 'Scrub Text';
  }
}

function renderLegend(legendData) {
  const legendEl = document.getElementById('legend');
  legendEl.innerHTML = ''; // Clear previous

  if (legendData.length === 0) {
    legendEl.textContent = 'No PII was found or scrubbed.';
    return;
  }

  // Add headers
  const headers = ['Type', 'Mock', 'Original'];
  headers.forEach(headerText => {
    const headerEl = document.createElement('div');
    headerEl.className = 'header';
    headerEl.textContent = headerText;
    legendEl.appendChild(headerEl);
  });

  // Add data rows
  legendData.forEach(item => {
    const typeEl = document.createElement('div');
    typeEl.textContent = item.type;
    const mockEl = document.createElement('div');
    mockEl.textContent = item.mock;
    const originalEl = document.createElement('div');
    originalEl.textContent = item.original;
    legendEl.appendChild(typeEl);
    legendEl.appendChild(mockEl);
    legendEl.appendChild(originalEl);
  });
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (navigator.clipboard) {
        navigator.clipboard.writeText(element.innerText).then(() => {
            alert('Copied to clipboard!');
        }).catch(err => {
            alert('Failed to copy.');
            console.error('Could not copy text: ', err);
        });
    }
}
