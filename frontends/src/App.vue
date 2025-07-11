<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import { SyncFromServer } from './utils/DataManager'
import Cookies from 'js-cookie'
import globalStore from './utils/GlobalStore'

onMounted(() => {
  if (Cookies.get("user_id")!=undefined)
    globalStore.UserID=Cookies.get("user_id");
  if (globalStore.UserID!=undefined&&globalStore.UserID!=-1)
    SyncFromServer();
})

const showInstallButton = ref(false)

onMounted(() => {
  // 检查是否可以安装PWA
  window.addEventListener('beforeinstallprompt', () => {
    showInstallButton.value = true
  })
})

function installPWA() {
  if (window.installPWA) {
    window.installPWA()
  }
}
</script>

<template>
  <div>
    <button v-if="showInstallButton" 
            @click="installPWA" 
            class="install-pwa-btn">
      安装应用
    </button>
    <RouterView />
  </div>
</template>

<style>
.install-pwa-btn {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 9999;
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
</style>