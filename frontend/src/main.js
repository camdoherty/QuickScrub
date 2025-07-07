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
  if (!document.getElementById('inputText').value || selectedTypes.length == 0) return alert('Input text and at least one PII type are required.');

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
