<template>
	<div class="form-container">
	  <h2>{{ t('login.title') }}</h2>
	  <h2 v-if="showGenerateQRCodeButton"><b>Please enter username</b></h2>
	  <form @submit.prevent="login">
		<div class="form-group">
		  <label for="username">{{ t('login.username') }}</label>
		  <input id="username" v-model="username" type="text" :placeholder="t('login.enterUsername')" required />
		</div>
		<div class="form-group" v-if="!hidePassword">
		  <label for="password">{{ t('login.password') }}</label>
		  <input id="password" v-model="password" type="password" :placeholder="t('login.enterPassword')" required />
		</div>
		<div class="form-group" v-if="!hideOTP">
		  <label for="otp">{{ t('login.otp') }}</label>
		  <input id="otp" v-model="otp" :placeholder="t('login.enterOTP')" required>
		</div>
		<button v-if="!hideSubmitButton" type="submit" class="submit-btn" :disabled="loading">
			{{ loading ? t('login.loading') : t('login.submit') }}
		</button>
		<a href="#" @click.prevent="generateQRCode" class="forgot-password-link">{{ t('login.getNewQR') }}</a>
	  </form>
	  <p v-if="error" class="message error">{{ error }}</p>
	  <div v-if="showQRCode">
		  <img :src="qrCode" :alt="t('login.qrCodeAlt')">
	  </div>
	  <button v-if="showGenerateQRCodeButton" class="submit-btn" @click="hideQRCode">{{ t('login.done') }}</button>
	</div>
  </template>
  
  <script>
  import router from '@/router';
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
		redirect: null,
		tfa: true,
		otp: '',
		showQRCode: false,
		qrCode: '',
		hidePassword: false,
		hideOTP: false,
		hideSubmitButton: false,
		showGenerateQRCodeButton: false,
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
					password: this.password,
					otp: this.otp
				})
			});
  
			const data = await response.json();
  
			if (response.ok && data.token) {
				await this.$store.dispatch('loginAction', {
				  accessToken: data.token,
				  refreshToken: data.refresh
				});
				
				this.password = '';
				await this.$nextTick();
				
				const redirectPath = this.redirect || '/profile';
				await this.$router.push(redirectPath);
			} else {
				this.error = this.ct('login.error.Login failed');
				this.password = '';
			}
		} catch (error) {
			console.error('Login error:', error);
			this.error = this.t('login.errors.Network error occurred');
			this.password = '';
		} finally {
			this.loading = false;
		}
	  },
  
	  async generateQRCode(){
		  this.hidePassword = true;
		  this.hideOTP = true;
		  this.hideSubmitButton = true;
		  this.showGenerateQRCodeButton = true;
		  try{
			  const response = await fetch('/api/auth/generate_qrcode/', {
				  method: 'POST',
				  headers: {
					  'Content-Type': 'application/json',
					  'Accept': 'application/json'
				  },
				  body: JSON.stringify({
					  username: this.username
				  })
			  });
  
			  const data = await response.json();
			  if (response.ok){
				  this.showQRCode = true;
				  this.qrCode = data.qr_code;
			  } else {
				  this.error = data.error || 'QR code generation failed';
			  }
		  } catch (error) {
			  console.error('QR code generation error: ', error);
			  this.error = 'Network error occured';
		  }
	  },
  
	  hideQRCode() {
		  this.showQRCode = false;
		  this.hidePassword = false;
		  this.hideOTP = false;
		  this.hideSubmitButton = false;
		  this.showGenerateQRCodeButton = false;
	  },
  
	  resetForm() {
		this.username = '';
		this.error = '';
		this.loading = false;
		this.otp = '',
		this.showQRCode = false;
		this.qrCode = '';
		this.showQRCode = false;
		this.hidePassword = false;
		this.hideOTP = false;
		this.hideSubmitButton = false;
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