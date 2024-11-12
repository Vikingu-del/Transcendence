import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Profile from '../views/Profile.vue';
import store from '../store'; // Ensure this path is correct

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
    }
  ]
});

// Add global navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.state.isAuthenticated;
  console.log(`Navigating to ${to.name}, isAuthenticated: ${isAuthenticated}`);

  if (to.meta.requiresAuth && !isAuthenticated) {
    // If not authenticated, redirect to login
    next({ name: 'Login' });
  } else if (!to.meta.requiresAuth && isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    // If authenticated, prevent access to login and register pages
    next({ name: 'Home' });
  } else {
    // If access is allowed, proceed to the route
    next();
  }
});

export default router;