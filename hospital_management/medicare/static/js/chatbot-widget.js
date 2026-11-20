(function () {
    function initialiseHospitalChat() {
        const chatWindow = document.getElementById("chatFloatWindow");
        const chatForm = document.getElementById("chatFloatForm");
        const chatInput = document.getElementById("chatFloatInput");
        const messages = document.getElementById("chatFloatMessages");
        const sendButton = document.getElementById("chatFloatSend");
        const endpoint = chatForm ? chatForm.dataset.url : "";
        const csrfInput = chatForm ? chatForm.querySelector('[name="csrfmiddlewaretoken"]') : null;
        const csrfToken = csrfInput ? csrfInput.value : "";

        if (!chatWindow || !chatForm || !chatInput || !messages || !sendButton) {
            console.warn("MediCare chat widget elements are missing from this page.");
            return;
        }

        const openers = [
            document.getElementById("chatFloatButton"),
            document.getElementById("chatFloatNavButton"),
            document.getElementById("chatFloatFooterButton")
        ].filter(Boolean);
        const closeButton = document.getElementById("chatFloatClose");

        function openChat() {
            chatWindow.classList.add("open");
            chatWindow.style.display = "flex";
            chatWindow.setAttribute("aria-hidden", "false");
            openers.forEach(button => button.setAttribute("aria-expanded", "true"));
            window.setTimeout(() => chatInput.focus(), 50);
        }

        function closeChat() {
            chatWindow.classList.remove("open");
            chatWindow.style.display = "none";
            chatWindow.setAttribute("aria-hidden", "true");
            openers.forEach(button => button.setAttribute("aria-expanded", "false"));
        }

        openers.forEach(button => button.addEventListener("click", function (event) {
            event.preventDefault();
            if (button.id === "chatFloatButton" && chatWindow.classList.contains("open")) closeChat();
            else openChat();
        }));
        if (closeButton) closeButton.addEventListener("click", closeChat);
        document.addEventListener("keydown", event => {
            if (event.key === "Escape" && chatWindow.classList.contains("open")) closeChat();
        });

        function addMessage(message, sender) {
            const bubble = document.createElement("div");
            bubble.classList.add("chat-float-message", sender === "user" ? "chat-float-user" : "chat-float-bot");
            bubble.textContent = message;
            messages.appendChild(bubble);
            messages.scrollTop = messages.scrollHeight;
            return bubble;
        }

        async function sendMessage(rawMessage) {
            const message = (rawMessage || "").trim();
            if (!message || sendButton.disabled) return;
            if (!endpoint) {
                addMessage("Chat service is not configured. Please contact the administrator.", "bot");
                return;
            }
            addMessage(message, "user");
            chatInput.value = "";
            chatInput.disabled = true;
            sendButton.disabled = true;
            const loading = addMessage("MediCare AI is typing...", "bot");
            try {
                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
                    body: JSON.stringify({ message })
                });
                const data = await response.json();
                loading.remove();
                if (!response.ok) throw new Error(data.reply || "The assistant could not respond.");
                addMessage(data.reply || "Sorry, I could not generate a response.", "bot");
            } catch (error) {
                loading.remove();
                addMessage(error.message || "Unable to connect to the AI assistant. Check that Django and Ollama are running.", "bot");
                console.error("MediCare chatbot:", error);
            } finally {
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
            }
        }

        chatForm.addEventListener("submit", event => {
            event.preventDefault();
            sendMessage(chatInput.value);
        });
        document.querySelectorAll(".chat-float-suggestions [data-question]").forEach(button => {
            button.addEventListener("click", () => sendMessage(button.dataset.question));
        });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialiseHospitalChat);
    else initialiseHospitalChat();
})();
