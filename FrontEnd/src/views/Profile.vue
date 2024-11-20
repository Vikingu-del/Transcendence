<template>
  <div class="profile-container">
    <h2>Profile</h2>
    <div class="profile-section">
      <img :src="avatarUrl" alt="User Avatar" />
      <form @submit.prevent="updateProfile" class="profile-form">
        <input
          v-model="displayName"
          :placeholder="displayNamePlaceholder"
          class="input-field"
          required
        />
        <input type="file" @change="onFileChange" class="file-input" />
        <button type="submit" class="btn primary-btn">Update Profile</button>
      </form>
    </div>
    <button @click="logout" class="btn secondary-btn">Logout</button>
  </div>
  <div>
      <h2>Debug Info</h2>
      <h1>{{ displayName }}</h1>
      <h1>{{ avatarUrl }}</h1>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      displayName: '',
      avatarUrl: '',
      avatarFile: null,
    };
  },
  async created() {
    await this.fetchProfile();
  },
  methods: {
    ...mapActions(['logoutAction']),
    async fetchProfile() {
      try {
        const response = await fetch('/profile/');
        if (response.ok) {
          const data = await response.json();
          this.displayName = data.display_name;
          this.avatarUrl = data.avatar;
        } else {
          alert('Failed to fetch profile');
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    },
    async logout() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        if (csrfToken) {
          await this.logoutAction({ csrftoken: csrfToken });
        } else {
          alert('CSRF token missing. Please refresh and try again.');
        }
      } catch (error) {
        alert('Logout failed. Please try again.');
      }
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + '=') {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    onFileChange(event) {
      this.avatarFile = event.target.files[0];
      if (this.avatarFile) {
        this.avatarUrl = URL.createObjectURL(this.avatarFile);
      }
    },
    async updateProfile() {
      const formData = new FormData();
      formData.append('display_name', this.displayName);
      // If there's a file for avatar, append it to the form data
      if (this.avatarFile) {
        formData.append('avatar', this.avatarFile);
      }

      const csrfToken = this.getCookie('csrftoken');

      try {
        const response = await fetch('/profile/', {
          method: 'PUT',
          headers: {
            'X-CSRFToken': csrfToken,
          },
          body: formData,
        });
        if (response.ok) {
          await this.fetchProfile();
        } else {
          alert('Failed to update profile');
        }
      } catch (error) {
        console.error('Error updating profile:', error);
      }
    },
  },
  computed: {
    displayNamePlaceholder() {
      return this.displayName ? this.displayName : 'Display Name';
    },
  },
};
</script>

<style scoped>
.profile-container {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.profile-section {
  margin-bottom: 20px;
}

.profile-picture {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #ddd;
  margin-bottom: 10px;
}

.profile-form {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.input-field,
.file-input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
  flex-grow: 1;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
}

.primary-btn {
  background-color: #4caf50;
  color: white;
}

.secondary-btn {
  background-color: #f44336;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}
</style>