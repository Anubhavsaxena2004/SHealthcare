import { getFAQResponse } from "./modules/faqEngine.js";
import { renderMessage, showTyping, removeTyping } from "./modules/renderEngine.js";
import { sendToAI } from "./modules/aiService.js";

const chatWindow = document.getElementById('chat-window');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatForm = document.querySelector('#chat-widget form');
const suggestionsContainer = document.getElementById('chat-suggestions');
const chatSendButton = document.getElementById('chat-send');

let isSending = false;

function syncSendState() {
    const hasText = !!(chatInput && chatInput.value && chatInput.value.trim().length > 0);
    if (chatSendButton) {
        chatSendButton.disabled = !hasText || isSending;
    }
}

// Toggle Chat Window
window.toggleChat = function () {
    chatWindow.classList.toggle('hidden');
    if (!chatWindow.classList.contains('hidden')) {
        chatWindow.classList.remove('scale-95', 'opacity-0');
        chatWindow.classList.add('scale-100', 'opacity-100');
        loadSuggestions();
        setTimeout(() => chatInput.focus(), 100);
        syncSendState();
    } else {
        chatWindow.classList.add('scale-95', 'opacity-0');
        chatWindow.classList.remove('scale-100', 'opacity-100');
    }
};

// Handle Message Submission
async function handleChatMore(message) {
    if (!message || isSending) return;
    isSending = true;
    syncSendState();

    // Render User Message
    renderMessage(chatMessages, { content: message, type: "text" }, "user");
    chatInput.value = '';
    syncSendState();

    // Check FAQ First
    const faqResponse = getFAQResponse(message);
    if (faqResponse) {
        setTimeout(() => {
            renderMessage(chatMessages, faqResponse, "bot");
            isSending = false;
            syncSendState();
        }, 500); // Small delay for natural feel
        return;
    }

    // Fallback to AI
    showTyping(chatMessages);
    try {
        const aiResponse = await sendToAI(message);
        removeTyping();
        renderMessage(chatMessages, aiResponse, "bot");
    } finally {
        isSending = false;
        syncSendState();
    }
}

// Event Listener for Form
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    handleChatMore(message);
});

// Enable/disable send button based on text
chatInput.addEventListener('input', syncSendState);
syncSendState();

// Load Suggestions
function loadSuggestions() {
    if (suggestionsContainer.children.length > 0) return;

    const suggestions = [
        "What is this website for?",
        "How accurately does it predict?",
        "Is my data secure?",
        "Take me to assessment"
    ];

    suggestions.forEach(text => {
        const btn = document.createElement('button');
        btn.className = "flex-shrink-0 bg-white border border-slate-200 text-slate-600 px-3 py-1.5 rounded-full text-xs hover:bg-medical-50 hover:text-medical-600 transition-colors whitespace-nowrap";
        btn.textContent = text;
        btn.onclick = () => {
            handleChatMore(text);
        };
        suggestionsContainer.appendChild(btn);
    });
}
