// Get data from the script tags
const messagerId = JSON.parse(document.getElementById('json-messager-id').textContent);
const receiverId = JSON.parse(document.getElementById('json-receiver-id').textContent);
const messagerUsername = JSON.parse(document.getElementById('json-messager-username').textContent);
const receiverUsername = JSON.parse(document.getElementById('json-receiver-username').textContent);

// Create WebSocket connection
const socket1 = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/' + receiverId + '/'
);

// Event listener for when the socket opens
socket1.onopen = function() {
    console.log("WebSocket connection opened successfully.");
};

// Event listener for receiving messages
socket1.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const message = data.message;
    const username = data.username;

    // Display the message
    displayMessage(username, message);
};

// Function to send a message
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;

    // Send the message through WebSocket
    socket1.send(JSON.stringify({
        'message': message,
        'username': messagerUsername,
        'receiver': receiverUsername
    }));

    messageInput.value = ''; // Clear input after sending
}

// Function to display the message
function displayMessage(username, message) {
    const chatBox = document.getElementById('chatBox');
    const messageElement = document.createElement('p');
    messageElement.textContent = `${username}: ${message}`;
    chatBox.appendChild(messageElement);
}

// Close the WebSocket when page is unloaded
window.onbeforeunload = function() {
    socket1.close();
};
    