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
          <div class="message-bubble">
            <span v-if="!message.loading">{{ message.text }}</span>
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
export default {
  name: "ChatBox",
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
</style>
