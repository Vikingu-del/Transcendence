import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Profile from '../views/Profile.vue';
import Chat from '../views/Chat.vue';
import store from '../store';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { requiresAuth: false }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile,
      meta: { requiresAuth: true }
    },
    {
      path: '/chat/:username',
      name: 'Chat',
      component: Chat,
      meta: { requiresAuth: true }
    }
  ]
});

// Add global navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.state.isAuthenticated;
  console.log(`Navigating to ${to.name}, isAuthenticated: ${isAuthenticated}`);

  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Redirecting to login page...');
    next({ name: 'Login' });
  } else if (!to.meta.requiresAuth && isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    console.log('Redirecting to home page...');
    next({ name: 'Home' });
  } else {
    console.log('Access granted to route:', to.name);
    next();
  }
});

export default router;