<template>
  <div class="LeftBar" style="height: 100%">
    <el-row>
      <el-col>
        <h1>
          Timer
          <el-button style="float: right" @click="logout()"
            ><b>登出</b></el-button
          >
        </h1>
        <el-menu class="MainMenu" router>
          <el-menu-item index="/dashboard" @click="Sync()">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/home" @click="Sync()">
            <el-icon><Document /></el-icon>
            <span>日程</span>
          </el-menu-item>
          <el-menu-item index="/deepseekchat" @click="Sync()">
            <el-icon><Setting /></el-icon>
            <span>对话</span>
          </el-menu-item>
          <el-menu-item index="/calendar" @click="Sync()">
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
import globalStore from "@/utils/GlobalStore";
import Cookies from "js-cookie";
import { useRouter } from "vue-router";
import router from "@/router";

export default {
  data ()  {
    return {
      router : useRouter()
    }
  },
  components: {
    SyncFromServer,
    Calendar,
    Monitor,
    Document,
    Setting,
  },
  methods: {
    Sync() {
      SyncFromServer();
    },
    logout () {
      Cookies.remove("user_id");
      globalStore.UserID=-1;
      this.router.push("login");
    },
  },
};
</script>

<style lang="less" scoped>
.el-menu {
  height: 90vh;
}
</style>
