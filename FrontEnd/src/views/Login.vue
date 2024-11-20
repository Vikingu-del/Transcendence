<template>
  <div class="form-container">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" placeholder="Enter username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" placeholder="Enter password" required />
      </div>
      <button type="submit" class="submit-btn">Login</button>
    </form>
    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="debugMessage" class="debug-message">{{ debugMessage }}</p>
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
      debugMessage: ''
    };
  },
  methods: {
    ...mapActions(['loginAction']),

    async login() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        const response = await this.loginAction({
          username: this.username,
          password: this.password,
          csrftoken: csrfToken
        });

        if (response.message === 'Login successful') {
          this.debugMessage = 'Login successful!';
          this.message = '';
        } else {
          this.message = response.message;
          this.debugMessage = '';
        }
      } catch (error) {
        this.message = response.message; /// to do 
        // this.debugMessage = `Error: ${error.message}`;
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

<style scoped>
.form-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

button.submit-btn {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

button.submit-btn:hover {
  background-color: #45a049;
}

.message, .debug-message {
  color: #f44336;
  text-align: center;
  margin-top: 10px;
}

.debug-message {
  color: #ff9800;
}
</style>