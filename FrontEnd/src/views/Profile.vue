<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2>Profile</h2>
      <div class="profile-section">
        <img :src="avatarUrl" alt="User Avatar" class="profile-picture" />
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
      <input v-model="searchQuery" @input="searchProfiles" placeholder="Search profiles...">
      <ul class="search-results">
        <li v-for="profile in searchResults" :key="profile.id" class="profile-item">
          <img :src="profile.avatar" alt="Avatar" class="profile-avatar" />
          <span class="profile-name">{{ profile.display_name }}</span>
        </li>
      </ul>
    </div>
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
      friends: [],
      searchQuery: '',
      searchResults: [],
    };
  },
  async created() {
    await this.fetchProfile();
  },
  methods: {
    ...mapActions(['logoutAction']),
    async fetchProfile() {
      try {
        const csrfToken = this.getCookie('csrftoken');
        const response = await fetch('/profile/', {
          headers: {
            'X-CSRFToken': csrfToken,
          },
        });
        console.log('Response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Profile data:', data);
          this.displayName = data.display_name;
          this.avatarUrl = data.avatar;
          this.friends = data.friends;
        } else {
          const errorText = await response.text();
          console.error('Fetch failed:', errorText);
          alert('Failed to fetch profile');
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        alert('Error fetching profile');
      }
    },
    async searchProfiles() {
      if (this.searchQuery.trim() === '') {
        this.searchResults = [];
        return;
      }
      try {
        const response = await fetch(`profile/search_profiles/?q=${this.searchQuery}`);
        if (response.ok) {
          const data = await response.json();
          console.log('Response data:', data);
          this.searchResults = data;
        } else {
          const errorText = await response.text();
          console.error('Fetch failed:', errorText);
        }
      } catch (error) {
        console.error('Error searching profiles:', error);
      }
    },
    async addFriend(friendId) {
      try {
        const response = await fetch('/add_friend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ friend_profile_id: friendId }),
        });
        if (response.ok) {
          alert('Friend added successfully');
          this.fetchProfile(); // Refresh friends list
        } else {
          console.error('Failed to add friend');
        }
      } catch (error) {
        console.error('Error adding friend:', error);
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
    filteredFriends() {
      return this.searchResults.length > 0 ? this.searchResults : this.friends;
    },
  },
};
</script>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.profile-card {
  padding: 20px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  margin-bottom: 20px;
}

.profile-section {
  margin-bottom: 20px;
}

.profile-picture {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #4caf50;
  margin-bottom: 10px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.input-field,
.file-input {
  padding: 10px;
  border: 1px solid #4caf50;
  border-radius: 5px;
  font-size: 14px;
  width: 100%;
}

.btn {
  padding: 10px 20px;
  border: 1px solid #4caf50;
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

.search-results {
  list-style: none;
  padding: 0;
}

.profile-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.profile-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 10px;
}

.profile-name {
  font-size: 16px;
}
</style>