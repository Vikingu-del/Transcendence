<template>
  <div class="form-container">
    <div v-if="!isRegistrationSuccessful">
      <h2>Register</h2>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            id="username" 
            v-model="username" 
            type="text" 
            placeholder="Enter username" 
            required 
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password" 
            v-model="password" 
            type="password" 
            placeholder="Enter password" 
            required 
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="passwordConfirm">Confirm Password</label>
          <input 
            id="passwordConfirm" 
            v-model="passwordConfirm" 
            type="password" 
            placeholder="Confirm password" 
            required 
            :disabled="loading"
          />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>
    </div>

    <div v-else class="success-container">
      <h2>Registration Successful!</h2>
      <p>Redirecting to login page...</p>
      <div class="loader"></div>
    </div>
    
    <p v-if="message" :class="['message', messageType]">{{ message }}</p>
    <ul v-if="errors.length" class="errors-list">
      <li v-for="error in errors" :key="error">{{ error }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      passwordConfirm: '',
      message: '',
      messageType: '',
      errors: [],
      loading: false,
      isRegistrationSuccessful: false
    };
  },
  methods: {
    resetForm() {
      this.username = '';
      this.password = '';
      this.passwordConfirm = '';
      this.message = '';
      this.messageType = '';
      this.errors = [];
      this.loading = false;
    },

    async register() {
      if (this.loading) return;
      
      this.loading = true;
      this.message = '';
      this.messageType = '';
      this.errors = [];

      // Client-side validation
      if (this.password !== this.passwordConfirm) {
        this.message = 'Passwords do not match!';
        this.messageType = 'error';
        this.loading = false;
        return;
      }

      try {
        const response = await fetch('/api/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password1: this.password,
            password2: this.passwordConfirm
          })
        });

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          // In the register method, update the success block:
          if (response.ok) {
            this.isRegistrationSuccessful = true;
            this.message = 'Registration successful! Redirecting to login...';
            this.messageType = 'success';
            // Clear sensitive data
            this.password = '';
            this.passwordConfirm = '';
            // Delay redirect to show success message
            setTimeout(() => {
              this.$router.push('/login');
            }, 1500);
          } else {
            this.message = data.error || 'Registration failed!';
            this.messageType = 'error';
            this.errors = data.details ? Object.values(data.details).flat() : [];
            // Clear passwords on error
            this.password = '';
            this.passwordConfirm = '';
          }
        } else {
          this.message = 'Unexpected response from server.';
          this.messageType = 'error';
          console.error('Non-JSON response:', await response.text());
        }
      } catch (error) {
        this.message = 'An error occurred. Please try again.';
        this.messageType = 'error';
        console.error(error);
      } finally {
        this.loading = false;
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
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

.message {
  text-align: center;
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
}

.message.error {
  color: #f44336;
  background-color: #ffebee;
}

.message.success {
  color: #4CAF50;
  background-color: #E8F5E9;
}

.errors-list {
  list-style: none;
  padding: 0;
  margin: 10px 0;
  color: #ff1100;
  background-color: #ffebee;
  border-radius: 4px;
  padding: 10px;
}

.errors-list li {
  margin: 5px 0;
  text-align: center;
}

.message {
  margin-top: 10px;
}

.message.error {
  margin-top: 10px;
  color: #f44336;
  background-color: #ffebee;
}

.success-container {
  text-align: center;
  padding: 20px;
}

.loader {
  display: inline-block;
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top: 3px solid #4CAF50;
  animation: spin 1s linear infinite;
  margin-top: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>