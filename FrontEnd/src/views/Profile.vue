<template>
	<div>
	  <h2>Profile</h2>
	  <form @submit.prevent="updateProfile">
		<input v-model="displayName" placeholder="Display Name" required />
		<input type="file" @change="onFileChange" />
		<button type="submit">Update Profile</button>
	  </form>
	  <form @submit.prevent="logout">
		<button type="submit">Logout</button>
	  </form>
	  <h2>Match History</h2>
	  <ul>
		<li v-for="match in matchHistory" :key="match.id">{{ match }}</li>
	  </ul>
	</div>
  </template>
  
  <script>
  import { mapActions } from 'vuex';
  
  export default {
	data() {
	  return {
		displayName: '',
		avatar: null,
		matchHistory: [],
		message: '', // Message to show after logout
		debugMessage: '' // Debugging message
	  };
	},
	async created() {
	  try {
		const response = await fetch('/profile/');
		const data = await response.json();
		this.displayName = data.display_name;
		this.matchHistory = data.match_history;
	  } catch (error) {
		console.error(error);
	  }
	},
	methods: {
	  ...mapActions(['logoutAction']), // Map the logoutAction from Vuex
  
	  // Handles the logout
	  async logout() {
		try {
			const csrfToken = this.getCookie('csrftoken');
			console.log('Retrieved CSRF Token:', csrfToken); // Debugging line
			// Continue with logout if the token is found
			if (csrfToken) {
				this.logoutAction({ csrftoken: csrfToken })
				.then(() => this.debugMessage = 'Logout successful!')
				.catch(error => this.message = 'Logout failed. Please try again.');
			} else {
				console.error('CSRF token not found');
				this.message = 'CSRF token missing. Please refresh and try again.';
			}
			
		} catch (error) {
			this.message = 'Logout failed. Please try again.';
			this.debugMessage = `Error: ${error.message}`;
		}
		},
		getCookie(name) {
		let cookieValue = null;
			if (document.cookie && document.cookie !== '') {
				const cookies = document.cookie.split(';');
				for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
				}
			}
			return cookieValue;
		},
	
	  // Handles the avatar file change
	  onFileChange(event) {
		this.avatar = event.target.files[0];
	  },
  
	  // Updates the user's profile
	  async updateProfile() {
		const formData = new FormData();
		formData.append('display_name', this.displayName);
		if (this.avatar) {
		  formData.append('avatar', this.avatar);
		}
		try {
		  const response = await fetch('/api/profile/', {
			method: 'PUT',
			body: formData
		  });
		  const data = await response.json();
		  console.log(data);
		} catch (error) {
		  console.error(error);
		}
	  }
	}
  };
  </script>
  