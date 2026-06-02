const API_URL = 'http://localhost:8000/api';

async function sendMessage() {
    const input = document.getElementById('userInput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    addMessage(msg, 'user');
    
    const btn = document.getElementById('sendBtn');
    btn.disabled = true;
    btn.innerHTML = '🤔 Thinking...';
    
    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        addMessage(data.final_response, 'assistant');
        if (data.function_called !== 'none') {
            addFunctionCall(data.function_called, data.tool_result);
        }
        showDebugSteps(data.steps);
    } catch (err) {
        addMessage('❌ Backend error. Make sure server is running on port 8000', 'system');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Send';
    }
}

function addMessage(text, type) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message ${type}-message`;
    div.innerHTML = `<strong>${type === 'user' ? '👤 You' : type === 'assistant' ? '🤖 AI' : 'ℹ️ System'}</strong><br>${text.replace(/\n/g, '<br>')}`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function addFunctionCall(name, result) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message function-call';
    div.innerHTML = `<strong>🔧 Tool called:</strong> ${name}<br><pre>${JSON.stringify(result, null, 2)}</pre>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showDebugSteps(steps) {
    const panel = document.getElementById('debugPanel');
    const stepsDiv = document.getElementById('debugSteps');
    if (steps && steps.length) {
        panel.style.display = 'block';
        stepsDiv.innerHTML = steps.map(s => `<div class="debug-step">${s}</div>`).join('');
    }
}

function toggleDebug() {
    const panel = document.getElementById('debugPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Health check on load
fetch(`${API_URL}/health`)
.then(r => r.json())
.then(data => {
    if (!data.openai_configured)
        addMessage('⚠️ OpenAI API key missing. Add to backend/.env', 'system');
    else
        addMessage('✅ Backend connected. Agent ready.', 'system');
})
