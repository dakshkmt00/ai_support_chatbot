const historyList = document.getElementById('historyList');
const messagesEl = document.getElementById('chatMessages');
const welcome = document.getElementById('welcome');
const input = document.getElementById('messageInput');
const form = document.getElementById('chatForm');
const sendBtn = document.getElementById('sendBtn');
const typing = document.getElementById('typing');
const charCount = document.getElementById('charCount');
let conversationId = null;
let busy = false;

function formatTime(iso) {
  try { return new Date(iso).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}); }
  catch { return ''; }
}
function escapeText(s) {
  return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')
    .replaceAll('"','&quot;').replaceAll("'","&#039;");
}
function showWelcome(show) { welcome.classList.toggle('hidden', !show); }
function addMessage(role, content, time = new Date().toISOString()) {
  showWelcome(false);
  const row = document.createElement('div');
  row.className = `message ${role === 'user' ? 'user' : 'assistant'}`;
  const avatar = document.createElement('div'); avatar.className = 'avatar'; avatar.textContent = role === 'user' ? 'You' : '✦';
  const wrap = document.createElement('div'); wrap.className = 'bubble-wrap';
  const bubble = document.createElement('div'); bubble.className = 'bubble'; bubble.textContent = content;
  const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = `${role === 'user' ? 'You' : 'Support AI'} · ${formatTime(time)}`;
  wrap.append(bubble, meta); row.append(avatar, wrap); messagesEl.append(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
async function refreshHistory() {
  try {
    const res = await fetch('/api/conversations');
    const data = await res.json();
    historyList.replaceChildren();
    if (!data.conversations.length) {
      const p = document.createElement('p'); p.className = 'muted'; p.textContent = 'No conversations yet'; historyList.append(p); return;
    }
    data.conversations.forEach(c => {
      const b = document.createElement('button'); b.className = 'history-item' + (c.id === conversationId ? ' active' : '');
      b.textContent = c.title || 'New conversation'; b.title = c.title;
      b.addEventListener('click', () => loadConversation(c.id)); historyList.append(b);
    });
  } catch { historyList.textContent = 'History unavailable'; }
}
async function loadConversation(id) {
  try {
    const res = await fetch(`/api/conversations/${id}/messages`);
    if (!res.ok) throw new Error('Could not load conversation');
    const data = await res.json(); conversationId = id; messagesEl.replaceChildren();
    data.messages.forEach(m => addMessage(m.role, m.content, m.created_at));
    showWelcome(data.messages.length === 0); await refreshHistory();
  } catch (e) { alert(e.message); }
}
function newConversation() { conversationId = null; messagesEl.replaceChildren(); showWelcome(true); refreshHistory(); input.focus(); }
async function sendMessage(text) {
  const message = (text ?? input.value).trim();
  if (!message || busy) return;
  if (message.length > 2000) { alert('Please keep your message under 2000 characters.'); return; }
  busy = true; sendBtn.disabled = true; input.value = ''; charCount.textContent = '0 / 2000';
  input.style.height = 'auto'; addMessage('user', message); typing.classList.remove('hidden');
  try {
    const res = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message, conversation_id:conversationId})});
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'The request failed. Please try again.');
    conversationId = data.conversation_id;
    addMessage('assistant', data.reply);
    await refreshHistory();
  } catch (e) { addMessage('assistant', `Sorry, something went wrong: ${e.message}`); }
  finally { typing.classList.add('hidden'); busy = false; sendBtn.disabled = false; input.focus(); }
}
form.addEventListener('submit', e => { e.preventDefault(); sendMessage(); });
input.addEventListener('input', () => { charCount.textContent = `${input.value.length} / 2000`; input.style.height='auto'; input.style.height=Math.min(input.scrollHeight,140)+'px'; });
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
document.getElementById('newChat').addEventListener('click', newConversation);
document.getElementById('clearBtn').addEventListener('click', async () => {
  if (conversationId === null) { newConversation(); return; }
  if (!confirm('Delete this conversation and its messages?')) return;
  try { const res = await fetch(`/api/conversations/${conversationId}`, {method:'DELETE'}); if (!res.ok) throw new Error('Unable to clear chat'); newConversation(); }
  catch(e) { alert(e.message); }
});
document.getElementById('exportBtn').addEventListener('click', () => { window.location.href='/api/export.csv'; });
document.querySelectorAll('[data-prompt]').forEach(b => b.addEventListener('click', () => sendMessage(b.dataset.prompt)));
refreshHistory();
