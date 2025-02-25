<template>
  <div class="form-container">
    <h2>{{ t('login.title') }}</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">{{ t('login.username') }}</label>
        <input 
          id="username" 
          v-model="username" 
          type="text" 
          :placeholder="t('login.enterUsername')" 
          required 
        />
      </div>
      <div class="form-group">
        <label for="password">{{ t('login.password') }}</label>
        <input 
          id="password" 
          v-model="password" 
          type="password" 
          :placeholder="t('login.enterPassword')" 
          required 
        />
      </div>
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? t('login.loading') : t('login.submit') }}
      </button>
    </form>
    <p v-if="error" class="message error">{{ t(`login.errors.${error}`) }}</p>
  </div>
</template>

<script>
import { auth } from '@/utils/auth';
import { useI18n } from 'vue-i18n';

export default {
  setup() {
    const { t } = useI18n();
    return { t };
  },
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      redirect: null
    };
  },
  
  created() {
    // Get redirect path from query params if it exists
    this.redirect = this.$route.query.redirect || '/profile';
  },

  methods: {
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
          console.log('Login response:', data);

          if (response.ok && data.token) {
              // Use auth helper instead of direct localStorage access
              await this.$store.dispatch('loginAction', data.token);
              
              this.password = '';
              await this.$nextTick();
              
              const redirectPath = this.redirect || '/profile';
              console.log('Redirecting to:', redirectPath);
              await this.$router.push(redirectPath);
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