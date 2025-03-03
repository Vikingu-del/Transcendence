// createRouter -> Factory function to create a router instance
// createWebHistory -> Factory function to create a history instance with HTML5 history API
import { createRouter, createWebHistory } from 'vue-router';
// Importing the views to which the router will navigate
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Profile from '../views/Profile.vue';
import Friends from '../views/Friends.vue';
import Notifications from '../views/Notifications.vue';
import LocalTournament from '../views/LocalTournament.vue'
import store from '@/store';

// Create the router instance and configuring the routes through this instance
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
    },
    {
      path: '/notifications',
      name: 'Notifications',
      component: Notifications,
      meta: { requiresAuth: true }
    },
    {
      path: '/local-tournament',
      name: 'LocalTournament',
      component: LocalTournament,
      meta: { requiresAuth: true }
    }
  ]
});

import { auth } from '@/utils/auth';

router.beforeEach(async (to, from, next) => {
  console.log('Route guard checking authentication');
  
  // Always proceed for non-auth routes
  if (!to.matched.some(record => record.meta.requiresAuth)) {
    console.log('Route does not require authentication, proceeding');
    return next();
  }

  // Check if this is a login route - never redirect from login to login
  if (to.path === '/login') {
    return next();
  }

  // For auth-required routes, check authentication status
  // CRITICAL FIX: Check localStorage again for a fresh token
  let token = localStorage.getItem('token');
  const refreshToken = localStorage.getItem('refreshToken');
  const isCurrentlyRefreshing = store.state.isRefreshing;
  
  // FIRST CHECK: If we have a valid token, immediately proceed
  if (token && !auth.isTokenExpired()) {
    console.log('User authenticated with valid token, proceeding');
    return next();
  }
  
  // SECOND CHECK: If refresh is already happening, wait briefly then check again
  if (isCurrentlyRefreshing) {
    console.log('Token is currently being refreshed, waiting briefly for completion...');
    
    // Wait a short time for the refresh to complete
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Re-check for token after waiting
    token = localStorage.getItem('token');
    if (token) {
      console.log('Token refresh completed during wait, proceeding with new token');
      return next();
    }
    
    console.log('Still no token after waiting, but refresh is in progress, proceeding anyway');
    return next();
  }
  
  // THIRD CHECK: If we have a refresh token but no valid access token, try to refresh
  if (refreshToken) {
    console.log('Token expired/missing but refresh token exists');
    
    try {
      console.log('Attempting to refresh token in route guard');
      // Set refreshing state to true
      store.commit('setIsRefreshing', true);
      
      // Refresh the token
      await store.dispatch('refreshToken');
      
      console.log('Token refresh succeeded in route guard');
      // Set isAuthenticated directly
      store.commit('setIsAuthenticated', true);
      
      // Short delay to ensure token is available
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Reset refreshing state
      store.commit('setIsRefreshing', false);
      
      // Proceed to the route after successful refresh
      return next();
    } catch (error) {
      console.error('Token refresh failed in route guard:', error);
      store.commit('setIsRefreshing', false);
      
      // Only redirect if refresh actually failed and we're not already going to login
      if (to.path !== '/login') {
        return next({
          path: '/login',
          query: { redirect: to.fullPath }
        });
      } else {
        return next();
      }
    }
  }
  
  // FINAL CHECK: No token and no refresh token - redirect to login
  console.log('No token and no refresh token, redirecting to login');
  return next({
    path: '/login',
    query: { redirect: to.fullPath }
  });
});

export default router;