


const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

function addMessage(sender, message, className) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", className);

    const senderElement = document.createElement("strong");
    senderElement.textContent = sender;

    const messageElement = document.createElement("p");
    messageElement.style.whiteSpace = "pre-line";
    messageElement.textContent = message;

    messageDiv.appendChild(senderElement);
    messageDiv.appendChild(messageElement);

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const question = userInput.value.trim();

    if (!question) {
        return;
    }

    addMessage("You", question, "user-message");
    userInput.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: question
            })
        });

        if (!response.ok) {
            throw new Error("Server returned an error.");
        }

        const data = await response.json();
        addMessage("UniMate 🤖", data.reply, "bot-message");

    } catch (error) {
        addMessage(
            "UniMate 🤖",
            "Sorry, I couldn't connect to the server. Please try again.",
            "bot-message"
        );
        console.error(error);
    }
});



