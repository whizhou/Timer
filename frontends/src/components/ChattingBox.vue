<template>
  <div class="chat-container" ref="chatContainer">
    <div class="messages-wrapper">
      <div
        class="message-item"
        v-for="(message, index) in messages"
        :key="index"
        :class="[
          message.align === 'left' ? 'message-left' : 'message-right',
          message.loading ? 'loading-message' : '',
        ]"
      >
        <div class="message-avatar" v-if="message.align === 'left'">
          <img src="https://www.deepseek.com/favicon.ico" alt="AI" />
        </div>
        <div class="message-avatar" v-else>
          <div class="user-avatar">用户</div>
        </div>
        <div class="message-content">
          <div v-if="checkSchedule(message.schedule)" class="message-bubble">
            <el-card>
              <template #header>
                <div class="card-header">
                <span v-if="message.schedule.content!=undefined"><b>{{ message.schedule.content.title }}</b></span>
                <span v-else><b>无题</b></span>
                   <edit-schedule :origin="message.schedule" @change="(newSchedule)=>message.schedule=newSchedule"></edit-schedule>
                  <el-button 
                    class="delete-btn" 
                    type="text" 
                    @click="deleteCards(message)"
                  >删除</el-button>
                </div>
              </template>
              <div class="card-content">
                <div v-for="(value, key) in message.schedule.content">
                  <div v-if="key != 'title' && Trans[key]!=undefined && value != ''">
                    <p v-if="value.constructor==Array">
                      <b>{{ Trans[key] }} : </b>{{ value[0] }} {{ value[1] }}
                    </p>
                    <p v-else>
                      <b>{{ Trans[key] }} : </b>{{ value }}
                    </p>
                  </div>
                </div>
              </div>
            </el-card>

          </div>
          <div class="message-bubble">
            <span v-if="!message.loading"><v-md-preview :text="message.text"></v-md-preview></span>
            <span v-else class="loading-dots">
              {{ message.text }}
              <span class="dot">.</span>
              <span class="dot">.</span>
              <span class="dot">.</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { DeleteSchedule } from '../utils/DataManager';
import EditSchedule from './EditSchedule.vue';
import Trans from "../utils/Trans.js"
import { cloneDeep } from 'lodash';
import { GetSchedule } from '../utils/DataManager';
import globalStore from '@/utils/GlobalStore';

export default {
  name: "ChatBox",
  data () {
    return {
      Trans
    }
  },
  components : {
    EditSchedule,
    GetSchedule,
  },
  props: {
    messages: {
      type: Array,
      required: true,
    },
  },
  mounted() {
    this.scrollToBottom();
  },
  updated() {
    this.scrollToBottom();
  },
  methods: {
    checkSchedule (schedule) {
      if (schedule==undefined) return false;
      // if (schedule.id==undefined) return false;
      // if (schedule.content.title==undefined) return false;
      return true;
    },
    deleteCards (message) {
      DeleteSchedule(message.schedule.id);
      message.schedule=undefined;
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
  },
};
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 10px 0;
  position: relative;
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: #a0c8ff #f0f5ff; /* Firefox */
}

/* 自定义滚动条样式 - Webkit浏览器 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: #f0f5ff;
}

.chat-container::-webkit-scrollbar-thumb {
  background-color: #a0c8ff;
  border-radius: 3px;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
  max-width: 90%;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-left {
  align-self: flex-start;
}

.message-right {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  border: 2px solid #e6f0ff;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar {
  width: 100%;
  height: 100%;
  background-color: #1890ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.message-content {
  display: flex;
  flex-direction: column;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  max-width: 600px;
  word-wrap: break-word;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  line-height: 1.6;
  font-size: 14px;
}

.message-left .message-bubble {
  background-color: #ffffff;
  border: 1px solid #e6f0ff;
  color: #333;
  border-top-left-radius: 4px;
  margin-right: 40px;
}

.message-right .message-bubble {
  background-color: #1890ff;
  color: white;
  border-top-right-radius: 4px;
  margin-left: 40px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.loading-message {
  position: relative;
}

.loading-dots .dot {
  opacity: 0;
  animation: loadingDot 1.4s infinite;
  display: inline-block;
}

.loading-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loadingDot {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.delete-btn {
  padding: 0;
  margin: 0;
}

.card-content {
  height: auto; /* 内容高度自适应 */
  overflow: hidden; /* 防止内容溢出 */
}

</style>
