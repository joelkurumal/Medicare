document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");
    const send = document.getElementById("sendButton");

    if (!form || !input || !messages || !send) return;

    const endpoint = form.dataset.url || "/chatbot-response/";
    const csrf = form.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

    function add(text, user = false) {
        const el = document.createElement("div");
        el.className = "chat-message " + (user ? "user-message" : "bot-message");
        el.textContent = text;
        messages.appendChild(el);
        messages.scrollTop = messages.scrollHeight;
        return el;
    }

    async function submitMessage(rawText) {
        const text = (rawText || "").trim();
        if (!text || send.disabled) return;

        add(text, true);
        input.value = "";
        send.disabled = true;
        input.disabled = true;
        const wait = add("MediCare AI is typing...");

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf
                },
                body: JSON.stringify({ message: text })
            });
            let data = {};
            try { data = await response.json(); }
            catch (_) { throw new Error("The server returned an unreadable response."); }
            wait.remove();
            if (!response.ok) throw new Error(data.reply || "Request failed.");
            add(data.reply || "No response received.");
        } catch (error) {
            wait.remove();
            add(error.message || "Unable to contact the assistant. Check Django and Ollama.");
            console.error("Chatbot error:", error);
        } finally {
            send.disabled = false;
            input.disabled = false;
            input.focus();
        }
    }

    form.addEventListener("submit", event => {
        event.preventDefault();
        submitMessage(input.value);
    });

    document.querySelectorAll(".suggestion-btn[data-question]").forEach(button => {
        button.addEventListener("click", () => submitMessage(button.dataset.question));
    });
});
