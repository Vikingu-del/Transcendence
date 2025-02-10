import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Profile from '../views/Profile.vue';
import Friends from '../views/Friends.vue';
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
      path: '/friends',
      name: 'Friends',
      component: Friends,
      meta: { requiresAuth: true }
    }
  ]
});

// Add global navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  const token = store.getters.getToken;
  console.log(`Navigating to ${to.name}, isAuthenticated: ${isAuthenticated}, hasToken: ${!!token}`);

  // Public routes that don't require auth
  if (to.matched.some(record => !record.meta.requiresAuth)) {
    if (isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      console.log('Authenticated user accessing login/register, redirecting to Profile');
      next({ name: 'Profile' });
    } else {
      console.log('Accessing public route:', to.name);
      next();
    }
    return;
  }

  // Protected routes
  if (!isAuthenticated || !token) {
    console.log('Unauthorized access attempt, redirecting to login');
    next({ 
      name: 'Login',
      query: { redirect: to.fullPath }
    });
    return;
  }

  console.log('Access granted to protected route:', to.name);
  next();
});

export default router;