<template>
    <div class="LeftBar" style="height: 100%;">
      <el-row>
        <el-col>
          <h1>Timer</h1>
          <el-menu class="MainMenu" router>
            <el-menu-item index="/">
              <el-icon><document /></el-icon>
              <span>日程</span>
            </el-menu-item>
            <el-menu-item index="/deepseekchat">
              <el-icon><setting /></el-icon>
              <span>对话</span>
            </el-menu-item>
            <el-menu-item index="/calendar">
              <el-icon><Calendar /></el-icon>
              <span>日历</span>
            </el-menu-item>
          </el-menu>
        </el-col>
      </el-row>
    </div>
</template>

<script lang="ts" setup>
import {
  Calendar,
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'
</script>

<style lang="less" scoped>
.el-menu{
    height:90vh
}
</style>