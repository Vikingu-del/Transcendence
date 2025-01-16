<template>
	<div class="chat-container">
	  <h2>Chat with {{ receiverUsername }}</h2>
	  <div class="chat-box">
		<div v-for="message in messages" :key="message.id" class="chat-message">
		  <span class="chat-username">{{ message.sender }}</span>: {{ message.content }}
		</div>
	  </div>
	  <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
	  <button @click="sendMessage">Send</button>
	</div>
  </template>
  
  <script>
  export default {
	data() {
	  return {
		messages: [],
		newMessage: '',
		socket: null,
		receiverUsername: this.$route.params.username,
	  };
	},
	created() {
	  this.connectWebSocket();
	},
	methods: {
	connectWebSocket() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		this.socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${this.receiverUsername}/`);
		this.socket.onmessage = (event) => {
		const message = JSON.parse(event.data);
		this.messages.push(message);
		};
		this.socket.onclose = () => {
		console.log('WebSocket connection closed');
		};
	},

	sendMessage() {
		if (this.newMessage.trim() !== '') {
		const message = {
			sender: this.$store.state.currentUser.username,
			content: this.newMessage,
		};
		this.socket.send(JSON.stringify(message));
		this.newMessage = '';
		}
	},
	},
  };
  </script>
  
  <style scoped>
  .chat-container {
	margin-top: 20px;
  }
  
  .chat-box {
	border: 1px solid #ccc;
	padding: 10px;
	height: 200px;
	overflow-y: scroll;
  }
  
  .chat-message {
	margin-bottom: 10px;
  }
  
  .chat-username {
	font-weight: bold;
  }
  
  input {
	width: 100%;
	padding: 10px;
	box-sizing: border-box;
  }
  </style>