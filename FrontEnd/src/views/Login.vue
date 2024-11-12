<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label>Username</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      username: '',
      password: '',
      message: ''
    };
  },
  methods: {
    ...mapActions(['loginAction']), // Rename the Vuex action to avoid conflict
    async login() {
      try {
        const response = await fetch('/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken') // Add CSRF token to headers
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          if (response.ok) {
            console.log('Login successful, calling loginAction...');
            this.loginAction(); // Call the Vuex login action
          } else {
            this.message = data.message || 'Invalid credentials';
          }
        } else {
          this.message = 'Unexpected response from server.';
          console.error('Non-JSON response:', await response.text());
        }
      } catch (error) {
        this.message = 'An error occurred. Please try again.';
        console.error(error);
      }
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  }
};
</script>