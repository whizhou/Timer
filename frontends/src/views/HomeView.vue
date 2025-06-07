<template>

  <div class = "homeview">

    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <Cards v-for="item in UserSchedules" :key="item.id" :cardData="item" />
        <div class="right-bottom"><create-schedule></create-schedule></div>
      </el-container>
    </el-container>

  </div>

</template>

<script>

import Cards from "../components/Cards.vue"
import CreateSchedule from "../components/CreateSchedule.vue"
import { UserSchedules } from "../components/DataManager"

export default {
  data () {
    return {
      UserSchedules
    }
  },
  components : {
    Cards,
    CreateSchedule
  }
}

</script>

<style>
.right-bottom {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 10px;
  }
</style>