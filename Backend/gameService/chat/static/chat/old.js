// Connect to the WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/online_users/');

// Wait for the WebSocket connection to open before handling messages
socket.onopen = function() {
    console.log("WebSocket connection opened successfully.");

    // Now you can receive messages from the WebSocket server
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'user_login') {
            // Add the user to the online list in the DOM, but exclude current user
            if (data.username !== currentUsername) {
                addUserToOnlineList(data.username);
            }
        } else if (data.type === 'user_logout') {
            // Remove the user from the online list in the DOM
            removeUserFromOnlineList(data.username);
        } else if (data.type === 'online_users_list') {
            // Initialize online users list, excluding the current user
            initializeOnlineUsersList(data.users);
        }
    };

    function initializeOnlineUsersList(users) {
        const onlineUsersContainer = document.getElementById("online-users");
        onlineUsersContainer.innerHTML = "";  // Clear the container

        // Add only users who are not the current user to the list
        users.forEach(user => {
            if (user !== currentUsername) {
                addUserToOnlineList(user);
            }
        });
    }

    function addUserToOnlineList(username) {
        const onlineUsersContainer = document.getElementById("online-users");
        
        // Check if the user is already in the list to avoid duplicates
        if (!document.getElementById(`${username}-online`)) {
            const userElement = document.createElement("p");
            userElement.id = `${username}-online`;  // Unique ID for each user
            userElement.textContent = `${username} is online `;
            
            // Create the chat and block links
            const chatLink = document.createElement("a");
            chatLink.href = `/${username}/`;  // Adjust the URL based on your routing
            chatLink.textContent = "chat";
            chatLink.setAttribute("data-username", username);
            
            const blockLink = document.createElement("a");
            blockLink.href = "#";
            blockLink.textContent = "block";
            
            // Append the chat and block links next to the user name
            userElement.appendChild(chatLink);
            userElement.appendChild(document.createTextNode(" | "));
            userElement.appendChild(blockLink);
            
            onlineUsersContainer.appendChild(userElement);
        }
    }
  

    // function addUserToOnlineList(username) {
    //     const onlineUsersContainer = document.getElementById("online-users");

    //     // Check if the user is already in the list to avoid duplicates
    //     if (!document.getElementById(`${username}-online`)) {
    //         const userElement = document.createElement("p");
    //         userElement.id = `${username}-online`;  // Unique ID for each user
    //         userElement.textContent = `${username} is online`;
            
    //         onlineUsersContainer.appendChild(userElement);
    //     }
    // }

    function removeUserFromOnlineList(username) {
        const userElement = document.getElementById(`${username}-online`);

        // Remove the user element from the DOM if it exists
        if (userElement) {
            userElement.remove();
        }
    }
};

// Handle any errors that occur with the WebSocket connection
socket.onerror = function(error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function() {
    console.log("WebSocket connection closed.");
};