import { getFAQResponse } from "./modules/faqEngine.js";
import { renderMessage, showTyping, removeTyping } from "./modules/renderEngine.js";
import { sendToAI } from "./modules/aiService.js";

const chatWindow = document.getElementById('chat-window');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatForm = document.querySelector('#chat-widget form');
const suggestionsContainer = document.getElementById('chat-suggestions');

// Toggle Chat Window
window.toggleChat = function () {
    chatWindow.classList.toggle('hidden');
    if (!chatWindow.classList.contains('hidden')) {
        chatWindow.classList.remove('scale-95', 'opacity-0');
        chatWindow.classList.add('scale-100', 'opacity-100');
        loadSuggestions();
        setTimeout(() => chatInput.focus(), 100);
    } else {
        chatWindow.classList.add('scale-95', 'opacity-0');
        chatWindow.classList.remove('scale-100', 'opacity-100');
    }
};

// Handle Message Submission
async function handleChatMore(message) {
    if (!message) return;

    // Render User Message
    renderMessage(chatMessages, { content: message, type: "text" }, "user");
    chatInput.value = '';

    // Check FAQ First
    const faqResponse = getFAQResponse(message);
    if (faqResponse) {
        setTimeout(() => {
            renderMessage(chatMessages, faqResponse, "bot");
        }, 500); // Small delay for natural feel
        return;
    }

    // Fallback to AI
    showTyping(chatMessages);
    const aiResponse = await sendToAI(message);
    removeTyping();
    renderMessage(chatMessages, aiResponse, "bot");
}

// Event Listener for Form
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    handleChatMore(message);
});

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
