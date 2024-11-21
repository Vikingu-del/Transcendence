<template>
  <div class="form-container">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" placeholder="Enter username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" placeholder="Enter password" required />
      </div>
      <button type="submit" class="submit-btn">Register</button>
    </form>
    <p v-if="message" class="message">{{ message }}</p>
    <ul v-if="errors.length" class="errors">
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
      message: '',
      errors: []
    };
  },
  methods: {
    async register() {
      try {
        const response = await fetch('/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password1: this.password,
            password2: this.password
          })
        });

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          if (response.ok) {
            this.message = 'Registration successful!';
            this.errors = [];
            this.$router.push('/login');
          } else {
            this.message = data.error || 'Registration failed!';
            this.errors = data.details ? Object.values(data.details).flat() : [];
          }
        } else {
          this.message = 'Unexpected response from server.';
          this.errors = [];
          console.error('Non-JSON response:', await response.text());
        }
      } catch (error) {
        this.message = 'An error occurred. Please try again.';
        this.errors = [];
        console.error(error);
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
  color: #f44336;
  text-align: center;
  margin-top: 10px;
}

.errors {
  color: #f44336;
  list-style-type: none;
  padding: 0;
  text-align: center;
}

.errors li {
  margin-top: 5px;
}
</style>