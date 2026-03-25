document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("chatbot-toggle");
    const closeBtn = document.getElementById("chatbot-close");
    const box = document.getElementById("chatbot-box");
    const input = document.getElementById("chatbot-input");
    const sendBtn = document.getElementById("chatbot-send");
    const messages = document.getElementById("chatbot-messages");
    const csrfToken = document.getElementById("chatbot-csrf-token").value;

    // Toggle open/close
    toggle.addEventListener("click", function () {
        box.classList.toggle("chatbot-hidden");
        if (!box.classList.contains("chatbot-hidden")) {
            input.focus();
        }
    });

    closeBtn.addEventListener("click", function () {
        box.classList.add("chatbot-hidden");
    });

    // Append a message bubble to the chat window
    function appendMessage(text, sender) {
        const div = document.createElement("div");
        div.classList.add("chat-msg");
        div.classList.add(sender === "user" ? "user-msg" : "bot-msg");
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    // Send message to Django backend
    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        input.value = "";
        input.disabled = true;
        sendBtn.disabled = true;

        try {
            const res = await fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ message: text }),
            });

            const data = await res.json();
            appendMessage(data.response || "Sorry, I didn't understand that.", "bot");
        } catch (err) {
            appendMessage("Sorry, something went wrong. Please try again.", "bot");
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});
