<script setup>

import { RouterLink, RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { SyncFromServer } from './utils/DataManager'

onMounted(() => {
  // SyncFromServer();
})

</script>

<template>
  <RouterView />
</template>