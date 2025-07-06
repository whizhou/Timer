// import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import LeftBar from './components/LeftBar.vue'
import ChatZone from './components/ChatZone.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Chat from "vue3-beautiful-chat"
import { registerSW } from 'virtual:pwa-register'

// 注册Service Worker并暴露更新和安装方法
const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    // 当有新版本时显示更新提示
    console.log('有新版本可用，请刷新')
    // 可以在这里添加UI提示，例如ElementPlus的消息提示
  },
  onOfflineReady() {
    // 当应用可以离线使用时
    console.log('应用已准备好离线使用')
  },
  onRegistered(r) {
    console.log('Service Worker已注册')
    // 将安装方法暴露到全局，方便调试
    window.installPWA = async () => {
      try {
        if ('BeforeInstallPromptEvent' in window) {
          console.log('尝试安装PWA')
          // 如果存在延迟的安装事件，使用它
          if (window.deferredPrompt) {
            window.deferredPrompt.prompt()
            const { outcome } = await window.deferredPrompt.userChoice
            console.log(`用户选择: ${outcome}`)
            window.deferredPrompt = null
          } else {
            console.log('没有可用的安装提示')
          }
        } else {
          console.log('此浏览器不支持PWA安装API')
        }
      } catch (error) {
        console.error('安装PWA时出错:', error)
      }
    }
  }
})

// 捕获beforeinstallprompt事件
window.deferredPrompt = null
window.addEventListener('beforeinstallprompt', (e) => {
  // 阻止Chrome 67及更早版本自动显示安装提示
  e.preventDefault()
  // 存储事件以便稍后触发
  window.deferredPrompt = e
  console.log('捕获到beforeinstallprompt事件')
})

const app = createApp(App)

var UserSchedules = []

app.provide("UserSchedules",UserSchedules)
app.config.globalProperties.$UserSchedules = UserSchedules;

app.component("leftbar",LeftBar)
app.component("chatzone",ChatZone)
app.use(ElementPlus)
app.use(router)
app.use(Chat)

app.mount('#app')

