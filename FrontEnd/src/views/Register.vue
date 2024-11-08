<template>
  <div class="container mt-5">
    <h2 class="mb-4">Register</h2>
    <form @submit.prevent="register" class="needs-validation" novalidate>
      <div class="form-group mb-3">
        <label for="username">Username</label>
        <input v-model="username" type="text" class="form-control" id="username" placeholder="Username" required />
        <div class="invalid-feedback">Please enter a username.</div>
      </div>
      <div class="form-group mb-3">
        <label for="email">Email</label>
        <input v-model="email" type="email" class="form-control" id="email" placeholder="Email" required />
        <div class="invalid-feedback">Please enter a valid email address.</div>
      </div>
      <div class="form-group mb-3">
        <label for="password1">Password</label>
        <input v-model="password1" type="password" class="form-control" id="password1" placeholder="Password" required />
        <div class="invalid-feedback">Please enter a password.</div>
      </div>
      <div class="form-group mb-3">
        <label for="password2">Confirm Password</label>
        <input v-model="password2" type="password" class="form-control" id="password2" placeholder="Confirm Password" required />
        <div class="invalid-feedback">Please confirm your password.</div>
      </div>
      <div class="form-group mb-3">
        <label for="display_name">Display Name</label>
        <input v-model="display_name" type="text" class="form-control" id="display_name" placeholder="Display Name" required />
        <div class="invalid-feedback">Please enter a display name.</div>
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
    </form>
    <p v-if="message" class="mt-3">{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      email: '',
      password1: '',
      password2: '',
      display_name: '',
      message: ''
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
            email: this.email,
            password1: this.password1,
            password2: this.password2,
            display_name: this.display_name
          })
        });
        const data = await response.json();
        if (response.ok) {
          this.message = 'Registration successful!';
          // Redirect to login page or update UI accordingly
          this.$router.push('/login');
        } else {
          this.message = data.message || 'Registration failed!';
        }
      } catch (error) {
        this.message = 'An error occurred. Please try again.';
        console.error(error);
      }
    }
  }
};
</script>

<style>
/* Add some custom styles if needed */
</style>