import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import DeepseekChat from "../views/DeepseekChat.vue";
import Calendar from "../views/Calendar.vue";
import Dashboard from "../views/Dashboard.vue";
import Login from "../views/Login.vue";
import Cookies from 'js-cookie'
import globalStore from "@/utils/GlobalStore";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
      meta: { requiresAuth: false },
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
    {
      path: "/dashboard",
      name: "dashboard",
      component: Dashboard,
    },
  ],
});

router.beforeEach((to, from, next) => {
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    
        const isAuthenticated = (globalStore.UserID!=undefined)&&(globalStore.UserID!=-1);
    
        if (!isAuthenticated) {
          if (Cookies.get("user_id")==undefined)
            next({name: 'login'});
          else {
            globalStore.UserID=Cookies.get("user_id");
            next();
          }
        } else {
          next()
        }

  } else {
    // 不需要认证的路由直接放行
    next()
  }
})

export default router;
