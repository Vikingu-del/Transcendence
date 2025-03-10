<template>
	<div class="form-container">
	  <div v-if="!isRegistrationSuccessful">
		<h2>{{ t('register.title') }}</h2>
		<form @submit.prevent="register">
		  <div class="form-group">
			<label for="username">{{ t('register.username') }}</label>
			<input 
			  id="username" 
			  v-model="username" 
			  type="text" 
			  :placeholder="t('register.usernamePlaceholder')"
			  required 
			  :disabled="loading"
			/>
		  </div>
		  <div class="form-group">
			  <label for="email">Email</label>
			  <input
				  id="email"
				  v-model="email"
				  type="text"
				  placeholder="Enter Email"
				  required
				  :disabled="loading"
			  />
		  </div>
		  <div class="form-group">
			<label for="password">{{ t('register.password') }}</label>
			<input 
			  id="password" 
			  v-model="password" 
			  type="password" 
			  :placeholder="t('register.passwordPlaceholder')"
			  required 
			  :disabled="loading"
			/>
		  </div>
		  <div class="form-group">
			<label for="passwordConfirm">{{ t('register.confirmPassword') }}</label>
			<input 
			  id="passwordConfirm" 
			  v-model="passwordConfirm" 
			  type="password" 
			  :placeholder="t('register.confirmPasswordPlaceholder')" 
			  required 
			  :disabled="loading"
			/>
		  </div>
		  <button type="submit" class="submit-btn" :disabled="loading">
			{{ loading ? this.t('register.loading') : this.t('register.submit') }}
		  </button>
		</form>
	  </div>
  
	  <div v-else class="success-container">
		<h2>{{ t('register.successTitle') }}</h2>
		<p>{{ t('register.redirecting') }}</p>
		<div class="loader"></div>
	  </div>
	  
	  <p v-if="message" :class="['message', messageType]">{{ message }}</p>
	  <ul v-if="errors.length" class="errors-list">
		<li v-for="error in errors" :key="error">{{ error }}</li>
	  </ul>
  
	  <div v-if="showQRCode">
		  <h2>{{ t('register.QRCode') }}</h2>
		  <img :src="qrCode" alt="2FA QR CODE">
		  <button type="submit" class="submit-btn" @click="redirectToLogin">{{ t('register.QRDone') }}</button>
	  </div>
  
	</div>
  </template>
  
  <script>
  
  import { SERVICE_URLS } from '@/config/services';
  import auth from '@/utils/auth';
  import { useI18n } from 'vue-i18n';
  
  export default {

	setup() {
    const { t } = useI18n();
    return { t };
  },

	data() {
	  return {
		username: '',
		email: '',
		password: '',
		passwordConfirm: '',
		message: '',
		messageType: '',
		errors: [],
		loading: false,
		isRegistrationSuccessful: false,
		showQRCode: '',
		qrCode: ''
	  };
	},
	methods: {
	  resetForm() {
		this.username = '';
		this.password = '';
		this.email = '';
		this.passwordConfirm = '';
		this.message = '';
		this.messageType = '';
		this.errors = [];
		this.loading = false;
		this.showQRCode = false;
	  },
  
	  async register() {
		try {
		  // 1. Register with auth service
		  const authResponse = await fetch('/api/auth/register/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
			  username: this.username,
			  email: this.email,
			  password1: this.password,
			  password2: this.passwordConfirm
			})
		  });
		  
		  const authData = await authResponse.json();
  
		  if (authResponse.ok) {
			  this.isRegistrationSuccessful = true;
			  // Clear sensitive data
			  this.password = '';
			  this.passwordConfirm = '';
			  this.showQRCode = true;
			  this.qrCode = authData.qr_code;
			// Delay redirect to show success message
		  } else {
			console.log('Cause: ', authData.details);
			// Handle auth service error
			if (authData.non_field_errors) {
			  this.errors = Array.isArray(authData.non_field_errors) 
				? authData.non_field_errors 
				: [authData.non_field_errors];
			} else if (authData.details) {
			  this.message = authData.details;
			} else {
			  this.message = this.t('register.messages.Registration failed');
			}
			this.messageType = 'error';
		  }
		} catch (error) {
		  this.message = 'Registration failed: ' + error.message;
		  this.messageType = 'error';
		} finally {
		  this.loading = false;
		}
	  },
	  redirectToLogin(){
		  this.message = this.t('register.messages.Redirecting');
		  this.messageType = 'success';
		  setTimeout(() => {
			  this.$router.push('/login');
		  }, 1500);
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