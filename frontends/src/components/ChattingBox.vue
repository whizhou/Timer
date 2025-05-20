<template>
  <div class="chat-container">
    <div
      class="message"
      v-for="(message, index) in messages"
      :key="index"
      :class="message.align === 'left' ? 'message-left' : 'message-right'"
    >
      {{ message.text }}
    </div>
  </div>
</template>
 
<script>
export default {
  name: "ChatBox",
  props : {
    messages : {
        type : Array,
        required : true
    }
  }
}
</script>
 
<style scoped>
.chat-container {
  width: 100%;
  margin: auto;
  padding: 40px;
  box-sizing: border-box;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
 
.message {
  width: 200px;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 15px;
  word-wrap: break-word;
}
 
.message-left {
  background-color: #42b983;
  align-self: flex-start;
}
 
.message-right {
  background-color: orange;
  align-self: flex-end;
}
</style>