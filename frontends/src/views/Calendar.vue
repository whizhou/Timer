<template>

  <div class = "calendar">
    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <el-calendar v-model="value" />
      </el-container>
    </el-container>
  </div>

</template>

<script lang="ts" setup>
import { ref } from 'vue'
const value = ref(new Date())
</script>