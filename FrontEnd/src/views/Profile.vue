<template>
	<div>
	  <h2>Profile</h2>
	  <form @submit.prevent="updateProfile">
		<input v-model="displayName" placeholder="Display Name" required />
		<input type="file" @change="onFileChange" />
		<button type="submit">Update Profile</button>
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
		const response = await fetch('/api/profile/');
		const data = await response.json();
		this.displayName = data.display_name;
		this.matchHistory = data.match_history;
	  } catch (error) {
		console.error(error);
	  }
	},
	methods: {
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