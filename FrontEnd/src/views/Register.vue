<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div>
        <label>Username</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Register</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      message: ''
    };
  },
  methods: {
    async register() {
      console.log(this.username, this.password);
      try {
        const response = await fetch('/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password1: this.password
          })
        });

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          if (response.ok) {
            this.message = 'Registration successful!';
            this.$router.push('/login');
          } else {
            this.message = data.message || 'Registration failed!';
          }
        } else {
          this.message = 'Unexpected response from server.';
          console.error('Non-JSON response:', await response.text());
        }
      } catch (error) {
        this.message = 'An error occurred. Please try again.';
        console.error(error);
      }
    }
  }
};
</script>