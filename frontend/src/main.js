import './style.css';

const PII_TYPES = [
  { tag: 'IP_ADDRESS', label: 'IP Address' }, { tag: 'EMAIL', label: 'Email' },
  { tag: 'PHONE', label: 'Phone Number' }, { tag: 'CREDIT_CARD', label: 'Credit Card' },
  { tag: 'MAC_ADDRESS', label: 'MAC Address' },
];

document.addEventListener('DOMContentLoaded', () => {
  // Populate Checkboxes
  const chkContainer = document.getElementById('pii-types-checkboxes');
  PII_TYPES.forEach(t => {
    const div = document.createElement('div');
    div.innerHTML = `<input type="checkbox" id="${t.tag}" value="${t.tag}" checked><label for="${t.tag}">${t.label}</label>`;
    chkContainer.appendChild(div);
  });

  // Event Listeners
  const inputTextEl = document.getElementById('inputText');
  inputTextEl.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault(); // Prevent new line in textarea
      handleScrub();
    }
  });
  
  document.getElementById('scrubButton').addEventListener('click', handleScrub);
  
  document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', () => handleCopy(button));
  });

  // Synchronized Scrolling
  const scrubbedTextEl = document.getElementById('scrubbedText');
  let activeScroller = null;

  const setActive = (el) => activeScroller = el;
  const syncScroll = (from, to) => {
    if (activeScroller === from) {
      to.scrollTop = from.scrollTop;
      to.scrollLeft = from.scrollLeft;
    }
  };

  inputTextEl.addEventListener('mouseenter', () => setActive(inputTextEl));
  scrubbedTextEl.addEventListener('mouseenter', () => setActive(scrubbedTextEl));

  inputTextEl.addEventListener('scroll', () => syncScroll(inputTextEl, scrubbedTextEl));
  scrubbedTextEl.addEventListener('scroll', () => syncScroll(scrubbedTextEl, inputTextEl));
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
  } finally {
    btn.disabled = false; btn.textContent = 'Scrub Text';
  }
}

function renderLegend(legendData) {
  const el = document.getElementById('legend');
  el.innerHTML = '';
  if (legendData.length === 0) return;

  const headers = ['Type', 'Mock', 'Original'];
  headers.forEach(h => { const d = document.createElement('div'); d.className = 'header'; d.textContent = h; el.appendChild(d); });
  legendData.forEach(i => {['type', 'mock', 'original'].forEach(k => { const d = document.createElement('div'); d.textContent = i[k]; el.appendChild(d); }); });
}

function getLegendTextForClipboard(element) {
  const children = Array.from(element.children);
  let text = '';
  const headers = children.slice(0, 3).map(c => c.textContent);
  text += headers.join('\t') + '\n';

  const rows = children.slice(3);
  for (let i = 0; i < rows.length; i += 3) {
    const row = rows.slice(i, i + 3).map(c => c.textContent);
    text += row.join('\t') + '\n';
  }
  return text.trim();
}

function handleCopy(button) {
  const targetId = button.dataset.copyTarget;
  const element = document.getElementById(targetId);
  if (navigator.clipboard && element) {
    const textToCopy = targetId === 'legend' ? getLegendTextForClipboard(element) : element.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalText = button.textContent;
      button.textContent = 'Copied!';
      setTimeout(() => {
        button.textContent = originalText;
      }, 2000); // Revert back after 2 seconds
    }).catch(err => console.error('Could not copy text: ', err));
  }
}
