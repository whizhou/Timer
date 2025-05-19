
<template>
  <div id="container" style="width:100%;height: 100%;">

    <div id="menu" style="height:100%;width:10%;float:left;">
      <leftbar></leftbar>  
    </div>
    
    <div id="content" style="background-color:#EEEEEE;height:80%;width:90%;float:right;">
      <ChattingBox :messages="messages"></ChattingBox>
    </div>

    <div id="input" style="background-color:#EEEEEE;height:20%;width:90%;float:right;">
        <el-input
          v-model="userinput"
          style="width: 100%;height: 60%;"
          :autosize="{ minRows: 4, maxRows: 4}"
          type="textarea"
          placeholder="请输入... ..."
        />
        <el-button type="success" @click="sendmessage">发送</el-button>
        <el-button type="danger" @click="cleanmessage">！清空消息！</el-button>
    </div>

  
  </div>
</template>

<script>
  import ChattingBox from '../components/ChattingBox.vue'
  import { cloneDeep } from "lodash"
  export default {
    components:{
      ChattingBox,
    },
    data() {
      return {
          messages: [
            { text: "你好！", align: "left" },
            { text: "你好！", align: "right" },
            { text: "功能开发中... ...", align: "left" },
          ],
          userinput : "",
      }
    },
    methods : {
      sendmessage () {
        if (this.userinput=="")
          return
        let addms=cloneDeep(this.userinput)
        this.userinput=""
        this.messages.push({text:addms, align:"right"});
        this.messages.push({text:"功能开发中... ...", align:"left"});
      },
      cleanmessage () {
        this.messages=[{ text: "你好！", align: "left" },]
      }
    }
  }

</script>

<style>
html,
body{
  height: 100%;
}
</style>