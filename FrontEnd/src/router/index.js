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
import Tournament from '@/views/Tournament.vue';

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
      path: '/tournament',
      name: 'Tournament',
      component: Tournament,
      meta: { requiresAuth: true }
    }
  ]
});

import { auth } from '@/utils/auth';

router.beforeEach((to, from, next) => {
    console.log('Route guard checking authentication');
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!auth.isAuthenticated() || auth.isTokenExpired()) {
            console.log('Authentication required or token expired, redirecting to login');
            next({
                path: '/login',
                query: { redirect: to.fullPath }
            });
        } else {
            console.log('User authenticated, proceeding to route');
            next();
        }
    } else {
        next();
    }
});

export default router;