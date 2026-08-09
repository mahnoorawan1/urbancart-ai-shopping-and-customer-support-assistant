const API_URL = "https://urbancart-ai-shopping-and-customer.onrender.com/chat";

const chatBody = document.getElementById("chatBody");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const themeToggle = document.getElementById("themeToggle");

// ================================
// Theme (Light / Dark)
// Persisted in localStorage so it
// survives a page reload.
// ================================

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    themeToggle.innerText = theme === "dark" ? "☀️" : "🌙";
    localStorage.setItem("urbancart-theme", theme);
}

(function initTheme() {
    const saved = localStorage.getItem("urbancart-theme");
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(saved || (prefersDark ? "dark" : "light"));
})();

themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
});

// ================================
// Session ID
// One per browser tab/reload — lets the
// backend remember what it already asked
// this customer across messages in the
// same conversation.
// ================================

const SESSION_ID = crypto.randomUUID();

// ================================
// Quick Actions — label -> message sent
// ================================

const quickMessages = {
    "Recommend Products": "I want a product recommendation.",
    "Track Order": "I want to track my order.",
    "Return Item": "I want to return my order.",
    "FAQs": "What services do you provide?",
    "Contact Support": "I want to speak with a human support representative."
};

// ================================
// Add Message Bubble
// ================================

function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add(sender);

    messageDiv.innerHTML = `
        <p>${message}</p>
    `;

    chatBody.appendChild(messageDiv);

    chatBody.scrollTop = chatBody.scrollHeight;
}

// ================================
// Quick Action Menu (re-appears after
// every bot reply so the customer can
// jump into another action without
// scrolling back up)
// ================================

function appendQuickMenu() {

    const existing = document.getElementById("dynamicQuickActions");
    if (existing) {
        existing.remove();
    }

    const menu = document.createElement("div");
    menu.classList.add("quick-actions");
    menu.id = "dynamicQuickActions";

    Object.keys(quickMessages).forEach(label => {

        const button = document.createElement("button");
        button.classList.add("quick-btn");
        button.innerText = label;

        button.addEventListener("click", () => {
            sendMessage(quickMessages[label]);
        });

        menu.appendChild(button);

    });

    chatBody.appendChild(menu);

    chatBody.scrollTop = chatBody.scrollHeight;
}

// ================================
// Typing Indicator
// ================================

function showTyping() {

    const typing = document.createElement("div");

    typing.classList.add("bot");

    typing.id = "typing";

    typing.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBody.appendChild(typing);

    chatBody.scrollTop = chatBody.scrollHeight;
}

function removeTyping() {

    const typing = document.getElementById("typing");

    if (typing) {

        typing.remove();

    }

}

// ================================
// Send Message
// ================================

async function sendMessage(message) {

    if (!message.trim()) return;

    const existingMenu = document.getElementById("dynamicQuickActions");
    if (existingMenu) {
        existingMenu.remove();
    }

    addMessage(message, "user");

    messageInput.value = "";

    showTyping();

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID
            })

        });

        const data = await response.json();

        removeTyping();

        addMessage(data.reply, "bot");

        appendQuickMenu();

    }

    catch (error) {

        removeTyping();

        addMessage(
            "Unable to connect to UrbanCart server. Please try again.",
            "bot"
        );

        console.error(error);

    }

}

// ================================
// Send Button
// ================================

sendBtn.addEventListener("click", () => {

    sendMessage(messageInput.value);

});

// ================================
// Enter Key
// ================================

messageInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage(messageInput.value);

    }

});

// ================================
// Static Quick Action Buttons (the
// original row shown on page load)
// ================================

document.querySelectorAll(".quick-btn").forEach(button => {

    button.addEventListener("click", () => {

        const text = button.innerText;

        sendMessage(quickMessages[text]);

    });

});

// ================================
// Auto Focus
// ================================

window.onload = () => {

    messageInput.focus();

};