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

import { auth } from '@/utils/auth';

router.beforeEach((to, from, next) => {
    console.log('Route guard checking authentication');
    
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!auth.isAuthenticated()) {
            console.log('Authentication required, redirecting to login');
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