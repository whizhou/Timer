<script setup>

import { RouterLink, RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { SyncFromServer } from './utils/DataManager'
import Cookies from 'js-cookie'
import globalStore from './utils/GlobalStore'

onMounted(() => {
  if (Cookies.get("user_id")!=undefined)
    globalStore.UserID=Cookies.get("user_id");
  if (globalStore.UserID!=undefined&&globalStore.UserID!=-1)
    SyncFromServer();
})

</script>

<template>
  <RouterView />
</template>