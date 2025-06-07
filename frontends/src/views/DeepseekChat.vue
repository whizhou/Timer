<template>

  <div class = "calendar">
    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <!-- container内为AI对话的实现区域 -->

        <!-- 示例：用ChattingBox实现有点样子的对话界面,可以换别的方式实现 -->
        <div id="content" style="background-color:#EEEEEE;height:80%;width:100%;float:right;">
          <ChattingBox :messages="messages"></ChattingBox>
        </div>

        <div id="input" style="background-color:#EEEEEE;height:20%;width:100%;float:right;">
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
        <!--  -->

      </el-container>
    </el-container>
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