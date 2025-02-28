<template>
  <div class="notifications-container">
    <h1 class="notifications-title">Notifications</h1>

    <div class="notification-actions">
      <button @click="markAllAsRead" class="mark-all-btn">
        Mark all as read
      </button>
    </div>

    <div class="notification-list">
      <div v-if="loading" class="loading">
        <span>Loading notifications...</span>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchNotifications" class="retry-btn">Retry</button>
      </div>

      <div v-else-if="notifications.length === 0" class="empty-state">
        <p>No notifications to display</p>
      </div>

      <div v-else>
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          :class="['notification-item', { 'unread': !notification.is_read }]"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-content">
            <p class="notification-message">{{ formatNotificationMessage(notification) }}</p>
            <p class="notification-time">{{ formatDate(notification.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue';
export default {
  name: 'Notifications',
  
  data() {
    return {
      notifications: [],
      loading: true,
      error: null,
      notificationService: null
    };
  },

  setup() {
    const notificationService = inject('notificationService');
    return { notificationService };
  },
  
  created() {
    this.fetchNotifications();
  },
  
  methods: {
    async fetchNotifications() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          this.$router.push('/login');
          return;
        }
        
        console.log('Fetching notifications with token:', token.substring(0, 10) + '...');
        
        const response = await fetch('/api/notification/', {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error('Failed to fetch notifications');
        }
        
        const data = await response.json();
        console.log('Notification data received:', data);
        
        this.notifications = data;
        this.loading = false;
      } catch (error) {
        console.error('Error fetching notifications:', error);
        this.error = 'Failed to load notifications. Please try again.';
        this.loading = false;
      }
    },
    
    async markAsRead(notificationId) {
      const notification = this.notifications.find(n => n.id === notificationId);
      if (notification && notification.is_read) return;
      
      try {
        const token = localStorage.getItem('token');
        
        const response = await fetch(`/api/notification/${notificationId}/read/`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to mark notification as read');
        }
        
        // Update local state
        this.notifications = this.notifications.map(notification => {
          if (notification.id === notificationId) {
            return { ...notification, is_read: true };
          }
          return notification;
        });
        if (this.notificationService) {
          this.notificationService.fetchUnreadCount();
        }
      } catch (error) {
        console.error('Error marking notification as read:', error);
      }
    },
    
    async markAllAsRead() {
      try {
        const token = localStorage.getItem('token');
        
        const response = await fetch('/api/notification/read-all/', {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json' 
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to mark all notifications as read');
        }
        
        // Update local state
        this.notifications = this.notifications.map(notification => {
          return { ...notification, is_read: true };
        });
        // Update the global notification count
        if (this.notificationService) {
          this.notificationService.fetchUnreadCount();
        }
      } catch (error) {
        console.error('Error marking all notifications as read:', error);
      }
    },
    
    formatNotificationMessage(notification) {
      console.log('Formatting notification:', notification);
      const senderName = notification.sender_name || 
                   (notification.content && notification.content.sender_name) || 
                   'Someone';
      // Adjusted to use notification_type instead of type based on your serializer
      switch (notification.notification_type) {
        case 'friend_request':
          return `${senderName} sent you a friend request`;
        case 'friend_accepted':
          return `${senderName} accepted your friend request`;
        case 'friend_declined':
          return `${senderName} declined your friend request`;
        case 'friend_removed':
          return `${senderName} removed you from their friends`;
        case 'game_invite':
          return `${senderName} invited you to play a game`;
        case 'game_accepted':
          return `${senderName} accepted your game invitation`;
        case 'game_declined':
          return `${senderName} declined your game invitation`;
        case 'chat_message':
          return `New message from ${notification.sender_name}`;
        default:
          if (typeof notification.content === 'object') {
            return notification.content.message || 'New notification';
          }
          return notification.content || 'New notification';
      }
    },
    
    formatDate(timestamp) {
      if (!timestamp) return '';
      
      const date = new Date(timestamp);
      const now = new Date();
      
      // Same day
      if (date.toDateString() === now.toDateString()) {
        return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      }
      
      // Yesterday
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      }
      
      // Older
      return `${date.toLocaleDateString()} at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
  }
};
</script>

<style scoped>
.notifications-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.notifications-title {
  text-align: center;
  margin-bottom: 20px;
  color: #ffffff;
}

.notification-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.mark-all-btn {
  padding: 8px 16px;
  background: #03a670;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.mark-all-btn:hover {
  background: #04d38e;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background: #2a2a2a;
}

.notification-item.unread {
  background: #2d2d2d;
  border-left: 4px solid #03a670;
}

.notification-message {
  margin: 0;
  color: #ffffff;
}

.notification-time {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #999999;
}

.loading, .error, .empty-state {
  padding: 20px;
  text-align: center;
  color: #999999;
}

.retry-btn, .load-more-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #03a670;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>