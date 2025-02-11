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

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    };
  },
  methods: {
    ...mapActions(['loginAction']),

    resetForm() {
      this.username = '';
      this.password = '';
      this.error = '';
      this.loading = false;
    },

    async login() {
      if (this.loading) return;
      
      this.loading = true;
      this.error = '';
      
      try {
        await this.loginAction({
          username: this.username,
          password: this.password
        });
        
        // Login successful - redirect handled in store
      } catch (error) {
        console.error('Login error:', error);
        if (error.response?.data?.message) {
          this.error = error.response.data.message;
        } else if (error.message) {
          this.error = error.message;
        } else {
          this.error = 'Login failed. Please try again.';
        }
        // Clear password on error
        this.password = '';
      } finally {
        this.loading = false; // Fixed: Set loading to false when done
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

.reset-btn {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  background-color: #666;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
}

.reset-btn:hover {
  background-color: #555;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}
</style>