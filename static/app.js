let messageCount = 0;
let currentUser = 'Rafael Nunes';

// ─── Utilities ────────────────────────────────────────────────

function getTime() {
    return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatResponse(text) {
    let html = escapeHtml(text);
    html = html
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    return `<p>${html}</p>`;
}

function buildSourcesBadges(fontes) {
    if (!fontes || fontes.length === 0) return '';
    const badges = fontes.map(f =>
        `<span class="source-badge">${escapeHtml(f)}</span>`
    ).join('');
    return `<div class="sources-row">📄 Fontes: ${badges}</div>`;
}

function buildEscalateButton() {
    return `
        <div class="escalate-row">
            <button class="escalate-btn" onclick="openTicket()">
                📝 Abrir chamado com o RH
            </button>
        </div>`;
}

function openTicket() {
    const input = document.getElementById('msgInput');
    input.value = 'Quero abrir um chamado com o RH.';
    input.focus();
    autoResize(input);
}

// ─── Message rendering ────────────────────────────────────────

function addMessage(content, isUser = false, extras = {}) {
    const area = document.getElementById('messagesArea');
    const indicator = document.getElementById('typingIndicator');

    let footer = '';
    if (!isUser) {
        footer += buildSourcesBadges(extras.fontes);
        if (extras.deve_escalar) {
            footer += buildEscalateButton();
        }
    }

    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
    div.innerHTML = `
        <div class="msg-avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="msg-body">
            <div class="msg-bubble">${content}${footer}</div>
            <span class="msg-time">${getTime()}</span>
        </div>
    `;
    area.insertBefore(div, indicator);
    area.scrollTop = area.scrollHeight;
}

function clearMessages() {
    const area = document.getElementById('messagesArea');
    const indicator = document.getElementById('typingIndicator');
    const welcome = document.getElementById('welcomeMsg');
    Array.from(area.children).forEach(child => {
        if (child !== welcome && child !== indicator) area.removeChild(child);
    });
    messageCount = 0;
}

function showTyping() {
    const indicator = document.getElementById('typingIndicator');
    indicator.style.display = 'flex';
    document.getElementById('messagesArea').scrollTop = 99999;
}

function hideTyping() {
    document.getElementById('typingIndicator').style.display = 'none';
}

// ─── History ──────────────────────────────────────────────────

async function loadHistory(usuario) {
    try {
        const res = await fetch(`/api/history/${encodeURIComponent(usuario)}`);
        const data = await res.json();
        if (!data.historico || data.historico.length === 0) return;

        data.historico.forEach(msg => {
            const isUser = msg.role === 'user';
            addMessage(
                isUser ? escapeHtml(msg.conteudo) : formatResponse(msg.conteudo),
                isUser
            );
        });

        messageCount = data.historico.filter(m => m.role === 'user').length;
    } catch {
        // No history yet — silent
    }
}

// ─── User switching ───────────────────────────────────────────

async function onUserChange() {
    const select = document.getElementById('userSelect');
    currentUser = select.value;
    clearMessages();
    await loadHistory(currentUser);
}

// ─── Send message ─────────────────────────────────────────────

async function sendMessage() {
    const input = document.getElementById('msgInput');
    const btn = document.getElementById('sendBtn');
    const text = input.value.trim();

    if (!text || btn.disabled) return;

    input.value = '';
    input.style.height = 'auto';
    btn.disabled = true;

    addMessage(escapeHtml(text), true);
    showTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mensagem: text,
                usuario: currentUser,
                contador_mensagens: messageCount,
            }),
        });

        const data = await res.json();
        hideTyping();

        if (data.resposta) {
            addMessage(formatResponse(data.resposta), false, {
                fontes: data.fontes || [],
                deve_escalar: data.deve_escalar || false,
            });
            messageCount++;
        } else if (data.detail) {
            addMessage(`<p>⚠️ ${escapeHtml(data.detail)}</p>`);
        } else {
            addMessage('<p>Desculpe, não consegui processar sua mensagem. Tente novamente.</p>');
        }
    } catch {
        hideTyping();
        addMessage('<p>⚠️ Erro de conexão. Verifique se o servidor está rodando.</p>');
    }

    btn.disabled = false;
    input.focus();
}

// ─── Clear all ────────────────────────────────────────────────

async function clearChat() {
    try {
        await fetch('/api/clear', { method: 'DELETE' });
    } catch { /* continua mesmo se falhar */ }
    clearMessages();
}

// ─── Input helpers ────────────────────────────────────────────

function handleKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 130) + 'px';
}

// ─── Init ─────────────────────────────────────────────────────

document.getElementById('welcomeTime').textContent = getTime();
loadHistory(currentUser);
