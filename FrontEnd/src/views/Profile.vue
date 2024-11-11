<template>
	<div>
	  <h2>Profile</h2>
	  <form @submit.prevent="updateProfile">
		<input v-model="displayName" placeholder="Display Name" required />
		<input type="file" @change="onFileChange" />
		<button type="submit">Update Profile</button>
	  </form>
	  <form @submit.prevent="handleLogout">
		<button type="submit">Logout</button>
	  </form>
	  <h2>Match History</h2>
	  <ul>
		<li v-for="match in matchHistory" :key="match.id">{{ match }}</li>
	  </ul>
	</div>
  </template>
  
  <script>

  export default {
	data() {
	  return {
		displayName: '',
		avatar: null,
		matchHistory: []
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
		async handleLogout() {
			try {
			// Send a POST request to the logout endpoint
			const response = await fetch('/logout/');
			
			if (response.status === 200) {
					// Remove the token from local storage
				localStorage.removeItem('token');
			
				// Clear user-related data from the application state
				if (this.$store) {
				this.$store.commit('clearUserData');
				} else {
					console.error('Vuex store not found.');
				}
				
				// Redirect the user to the login page
				if (this.$router) {
				this.$router.push('/login/');
				} else {
				console.error('Vue router not found.');
				}
				
				// Optionally, show a notification or message
				if (this.$toast) {
				this.$toast.success('You have been logged out successfully.');
				} else {
				console.error('Vue toast not found.');
				}
			} else {
				console.error('Logout failed:', response.data.message);
			}
			} catch (error) {
				console.error('An error occurred during logout:', error);
			}
  		},
		onFileChange(event) {
			this.avatar = event.target.files[0];
		},
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