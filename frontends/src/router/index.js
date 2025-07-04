import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import DeepseekChat from "../views/DeepseekChat.vue";
import Calendar from "../views/Calendar.vue";
import Dashboard from "../views/Dashboard.vue";
import Login from "../views/Login.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: Login,
      meta: { requiresAuth: false },
    },
    {
      path: "/home",
      name: "home",
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: "/deepseekchat",
      name: "deepseekchat",
      component: DeepseekChat,
      meta: { requiresAuth: true },
    },
    {
      path: "/calendar",
      name: "calendar",
      component: Calendar,
      meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: Dashboard,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, from, next) => {
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    
    const isAuthenticated = checkAuthStatus()
    
    if (!isAuthenticated) {
      // 未登录则重定向到登录页
      next({name: 'login'});
    } else {
      next()
    }
  } else {
    // 不需要认证的路由直接放行
    next()
  }
})

import Cookies from 'js-cookie'

function checkAuthStatus() {
  // const token = Cookies.get('session');
  // return token
  return true;
}

export default router;
