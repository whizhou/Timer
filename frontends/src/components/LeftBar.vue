<template>
  <div class="LeftBar" style="height: 100%">
    <el-row>
      <el-col>
        <h1>
          Timer<el-button style="float: right" @click="Sync()"
            ><b>测试：同步</b></el-button
          >
        </h1>
        <el-menu class="MainMenu" router>
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/">
            <el-icon><Document /></el-icon>
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

<script lang="ts">
import {
  Calendar,
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  Monitor,
} from "@element-plus/icons-vue";

import { SyncFromServer } from "../utils/DataManager";

export default {
  components: {
    SyncFromServer,
  },
  methods: {
    Sync() {
      SyncFromServer();
    },
  },
};
</script>

<style lang="less" scoped>
.el-menu {
  height: 90vh;
}
</style>
