<template>
	<div>
	  <h2>Friends List</h2>
	  <ul>
		<li v-for="friend in friends" :key="friend.id">{{ friend.friend.username }} - {{ friend.friend.userprofile.display_name }}</li>
	  </ul>
	</div>
  </template>
  
  <script>
  export default {
	data() {
	  return {
		friends: []
	  };
	},
	async created() {
	  try {
		const response = await fetch('/api/friends/');
		const data = await response.json();
		this.friends = data;
	  } catch (error) {
		console.error(error);
	  }
	}
  };
  </script>