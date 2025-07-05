// import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import LeftBar from './components/LeftBar.vue'
import ChatZone from './components/ChatZone.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Chat from "vue3-beautiful-chat"
// import VueCookies from 'vue-cookies'

import VMdPreview from '@kangc/v-md-editor/lib/preview';
import '@kangc/v-md-editor/lib/style/preview.css';
import githubTheme from '@kangc/v-md-editor/lib/theme/github.js';
import '@kangc/v-md-editor/lib/theme/style/github.css';

// highlightjs
import hljs from 'highlight.js';

VMdPreview.use(githubTheme, {
  Hljs: hljs,
});

const app = createApp(App)

var UserSchedules = []

app.provide("UserSchedules",UserSchedules)
app.config.globalProperties.$UserSchedules = UserSchedules;

app.component("leftbar",LeftBar)
app.component("chatzone",ChatZone)
app.use(ElementPlus)
app.use(router)
app.use(Chat)
// app.use(VueCookies)
app.use(VMdPreview)

app.mount('#app')

