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
    <!-- <form v-if="tfa" @submit.prevent="verifyTFA"> // for walid
      <label for="ottp">Username</label> // for walid
        <input id="ottp" v-model="username" type="digit" placeholder="Enter the code" required /> // for walid
    </form>>   //for walid -->  
  </div>
</template>

<script>
import router from '@/router';
import { auth } from '@/utils/auth';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      redirect: null,
      // tfa: true, for walid
    };
  },
  
  created() {
    // Get redirect path from query params if it exists
    this.redirect = this.$route.query.redirect || '/profile';
  },

  methods: {
    // async verifyTFA() { // for walid
    //   try {
    //       const response = await fetch('/api/auth/login/', {
    //           method: 'POST',
    //           headers: { 
    //               'Content-Type': 'application/json',
    //               'Accept': 'application/json'
    //           },
    //           body: JSON.stringify({
    //               username: this.username,
    //               password: this.password
    //           })
    //       });
    //       await router.push('/profile');
    //     } catch (error) {
    //       console.error('Login error:', error);
    //       this.error = 'Network error occurred';
    //       this.password = '';
    //     } finally {
    //       this.loading = false;
    //     }  
    // },
    async login() {
      if (this.loading) return;
      this.loading = true;
      this.error = '';
      
      try {
          const response = await fetch('/api/auth/login/', {
              method: 'POST',
              headers: { 
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
              },
              body: JSON.stringify({
                  username: this.username,
                  password: this.password
              })
          });

          const data = await response.json();
          console.log('Login response WE ARE HERE:', data);

          if (response.ok && data.token) {
              await this.$store.dispatch('loginAction', {
                accessToken: data.token,
                refreshToken: data.refresh
              });
              
              this.password = '';
              await this.$nextTick();
              
              const redirectPath = this.redirect || '/profile';
              console.log('Redirecting to:', redirectPath);
              await this.$router.push(redirectPath);
              // tfa = true;
          } else {
              this.error = data.error || 'Login failed';
              this.password = '';
          }
      } catch (error) {
          console.error('Login error:', error);
          this.error = 'Network error occurred';
          this.password = '';
      } finally {
          this.loading = false;
      }
    },

    resetForm() {
      this.username = '';
      this.password = '';
      this.error = '';
      this.loading = false;
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