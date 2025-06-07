<template>

  <div class = "homeview">

    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <Cards :cards="globalStore.UserSchedules" />
        <div class="right-bottom"><create-schedule></create-schedule></div>
      </el-container>
    </el-container>

  </div>

</template>

<script>

import Cards from "../components/Cards.vue"
import CreateSchedule from "../components/CreateSchedule.vue"
import globalStore from "../utils/GlobalStore.js"
// import { GetDataFromServer } from "../utils/DataManager";
// import { serverURL } from "../utils/DataManager";

export default {
  data () {
    return {
      globalStore,
      // serverURL,
    }
  },
  components : {
    Cards,
    CreateSchedule,
    // GetDataFromServer,
  },
  // mounted () {
  //   let init = GetDataFromServer(serverURL+"schedule/");
  //   if (init==undefined)
  //     console.log("server error");
  //   else globalStore.UserSchedules=init;
  // }
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