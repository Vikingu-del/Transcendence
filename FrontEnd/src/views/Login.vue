<template>
  <div>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" />
      <input v-model="password" type="password" placeholder="Password" />
      <button type="submit">Login</button>
    </form>
    <p v-if="message">{{ message }}</p>
    <p v-if="debugMessage" style="color: red;">{{ debugMessage }}</p> <!-- Display debug message -->
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      username: '',
      password: '',
      message: '',
      debugMessage: '' // Debugging message
    };
  },
  methods: {
    ...mapActions(['loginAction']), // Map the loginAction from Vuex

    async login() {
      try {
        const csrfToken = this.getCookie('csrftoken'); // Get CSRF token

        // Call the Vuex action to login
        await this.loginAction({
          username: this.username,
          password: this.password,
          csrftoken: csrfToken
        });

        this.debugMessage = 'Login successful!';
      } catch (error) {
        this.message = 'Login failed. Please try again.';
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
    }
  }
};
</script>
