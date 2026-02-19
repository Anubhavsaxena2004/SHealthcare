export async function sendToAI(message) {
    try {
        const response = await fetch('/api/general-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        return {
            content: data.reply || "I'm having trouble thinking right now.",
            type: "text"
        };

    } catch (error) {
        console.error("AI Service Error:", error);
        return {
            content: "I'm having trouble connecting to the server. Please check your internet or try again later.",
            type: "text"
        };
    }
}
