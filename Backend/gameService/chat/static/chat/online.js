const socket = new WebSocket('ws://localhost:8000/ws/online_users/');

socket.onopen = function() {
    console.log("WebSocket connection opened successfully.");

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'user_login') {
            if (data.username !== currentUsername) {
                updateUserStatus(data.username, "online"); 
            }
        } else if (data.type === 'user_logout') {
            if (data.username !== currentUsername) {
                updateUserStatus(data.username, "");
            }
        } else if (data.type === 'online_users_list') {
            initializeOnlineUsersList(data.users);
        }
    };

    function initializeOnlineUsersList(users) {
        users.forEach(user => {
            if (user !== currentUsername) {
                updateUserStatus(user, "online");  
            }
        });
    }

    function updateUserStatus(username, status) {
        const statusTag = document.getElementById(`${username}_tag`);
        const playTag = document.getElementById(`${username}_play`);
    
        if (statusTag && playTag) {
            if (status === "online") {
                playTag.textContent = "play";
            } else {
                playTag.textContent = ""; // Remove "Play" when offline
            }
            statusTag.textContent = status;
        } else {
            console.warn(`Element for user ${username} not found.`);
        }
    }
};

socket.onerror = function(error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function() {
    console.log("WebSocket connection closed.");
};
