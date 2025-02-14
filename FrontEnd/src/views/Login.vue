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
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
    <p v-if="error" class="message error">{{ error }}</p>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { getAuthEndpoints, getBaseUrl } from '@/services/ApiService';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      authEndpoints: null
    };
  },
  created() {
    const baseUrl = getBaseUrl();
    this.authEndpoints = getAuthEndpoints(baseUrl);
  },
  methods: {
    ...mapActions(['loginAction']),

    async login() {
      if (this.loading) return;
      this.loading = true;
      this.error = '';
      
      try {
        await this.loginAction({
          username: this.username,
          password: this.password
        });
        // Redirect to home page after successful login
        this.$router.push('/');
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message || 'Login failed. Please try again.';
      } finally {
        this.loading = false;  // Fixed: Was setting to true instead of false
      }
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

.error {
  color: #f44336;
  text-align: center;
  margin-top: 10px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>