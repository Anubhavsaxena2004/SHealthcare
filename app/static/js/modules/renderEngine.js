export function renderMessage(container, response, sender = "bot") {
    const messageDiv = document.createElement("div");
    messageDiv.className = `flex flex-col space-y-1 fade-in ${sender === 'user' ? 'items-end' : 'items-start'}`;

    let innerHTML = '';

    if (sender === 'user') {
        innerHTML = `
            <div class="flex items-end justify-end">
                <div class="bg-medical-600 text-white px-4 py-2 rounded-2xl rounded-br-sm shadow-md text-sm max-w-[85%]">
                    ${response.content}
                </div>
            </div>
        `;
    } else {
        // Bot Message Container
        let contentHTML = '';

        if (response.type === "text") {
            contentHTML = response.content;
        } else if (response.type === "navigation") {
            contentHTML = `
                <p class="mb-2">${response.content}</p>
                <button 
                    onclick="window.location.href='${response.action}'"
                    class="flex items-center space-x-2 bg-gradient-to-r from-medical-600 to-teal-500 text-white px-4 py-2 rounded-lg hover:shadow-md transition-all text-xs font-semibold transform hover:scale-105"
                >
                    <span>Click to Proceed</span>
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                </button>
            `;
        } else if (response.type === "list") {
            contentHTML = `
                <ul class="list-disc pl-4 space-y-1">
                    ${response.items.map(item => `<li>${item}</li>`).join('')}
                </ul>
            `;
        }

        innerHTML = `
            <div class="flex items-end">
                <div class="w-6 h-6 bg-medical-100 rounded-full flex items-center justify-center text-xs text-medical-600 font-bold mr-2 mb-1 flex-shrink-0">AI</div>
                <div class="bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm text-sm text-slate-700 max-w-[85%] border border-slate-100">
                    ${contentHTML}
                </div>
            </div>
        `;
    }

    messageDiv.innerHTML = innerHTML;
    container.appendChild(messageDiv);

    // Smooth scroll to new message
    setTimeout(() => {
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 50);
}

export function showTyping(container) {
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
    container.appendChild(div);
    setTimeout(() => {
        div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 50);
}

export function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}
