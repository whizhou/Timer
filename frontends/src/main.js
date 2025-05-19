// import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import LeftBar from './components/LeftBar.vue'
import ChatZone from './components/ChatZone.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Chat from "vue3-beautiful-chat"

const app = createApp(App)

app.component("leftbar",LeftBar)
app.component("chatzone",ChatZone)
app.use(ElementPlus)
app.use(router)
app.use(Chat)

app.mount('#app')

