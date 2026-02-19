const chatWindow = document.getElementById('chat-window');
const chatMessages = document.getElementById('chat-messages');

function toggleChat() {
    chatWindow.classList.toggle('hidden');
    if (!chatWindow.classList.contains('hidden')) {
        chatWindow.classList.remove('scale-95', 'opacity-0');
        chatWindow.classList.add('scale-100', 'opacity-100');
        // Load suggestions on open
        loadSuggestions();
    } else {
        chatWindow.classList.add('scale-95', 'opacity-0');
        chatWindow.classList.remove('scale-100', 'opacity-100');
    }
}

async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Add User Message
    addMessage(message, 'user');
    input.value = '';

    // Show Typing Indicator
    showTyping();

    try {
        const response = await fetch('/api/general-chat', { // Corrected endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        removeTyping();

        if (data.reply) {
            addMessage(data.reply, 'ai');
        } else {
            addMessage("I'm sorry, I couldn't process that.", 'ai');
        }

    } catch (error) {
        removeTyping();
        addMessage("Connection error. Please try again.", 'ai');
    }
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = 'flex flex-col space-y-1 fade-in';

    if (sender === 'user') {
        div.innerHTML = `
            <div class="flex items-end justify-end">
                <div class="bg-medical-600 text-white px-4 py-2 rounded-2xl rounded-br-sm shadow-md text-sm max-w-[85%]">
                    ${text}
                </div>
            </div>
        `;
    } else {
        div.innerHTML = `
            <div class="flex items-end">
                <div class="w-6 h-6 bg-medical-100 rounded-full flex items-center justify-center text-xs text-medical-600 font-bold mr-2 mb-1">AI</div>
                <div class="bg-white px-4 py-2 rounded-2xl rounded-bl-sm shadow-sm text-sm text-slate-700 max-w-[85%] border border-slate-100">
                    ${text}
                </div>
            </div>
        `;
    }

    chatMessages.appendChild(div);
    // Scroll to the new message
    setTimeout(() => {
        div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 50);
}

function showTyping() {
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'flex items-end fade-in';
    div.innerHTML = `
        <div class="w-6 h-6 bg-medical-100 rounded-full flex items-center justify-center text-xs text-medical-600 font-bold mr-2 mb-1">AI</div>
        <div class="bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm border border-slate-100 flex space-x-1">
            <div class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
            <div class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-100"></div>
            <div class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-200"></div>
        </div>
    `;
    chatMessages.appendChild(div);
    setTimeout(() => {
        div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 50);
}

function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

async function loadSuggestions() {
    // Only load if empty
    const suggestionsContainer = document.getElementById('chat-suggestions');
    if (suggestionsContainer.children.length > 0) return;

    // Static suggestions for now to save API calls, or fetch from endpoint
    const suggestions = [
        "I'm feeling anxious",
        "How to prevent diabetes?",
        "Heart health tips",
        "Interpret my results"
    ];

    suggestions.forEach(text => {
        const btn = document.createElement('button');
        btn.className = "flex-shrink-0 bg-white border border-slate-200 text-slate-600 px-3 py-1.5 rounded-full text-xs hover:bg-medical-50 hover:text-medical-600 transition-colors whitespace-nowrap";
        btn.textContent = text;
        btn.onclick = () => {
            document.getElementById('chat-input').value = text;
            handleChatSubmit(new Event('submit'));
        };
        suggestionsContainer.appendChild(btn);
    });
}
