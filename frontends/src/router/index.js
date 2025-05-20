import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DeepseekChat from '../views/DeepseekChat.vue'
import Calendar from '@/views/Calendar.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/dpchat',
      name: 'deepseekchat',
      component: DeepseekChat,
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: Calendar,
    },
  ],
})

export default router
