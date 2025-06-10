<template>
  <div class="chat-page">
    <el-container>
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <div class="app-logo">
            <img src="https://www.deepseek.com/favicon.ico" alt="Logo" />
            <h2>Timer</h2>
          </div>
        </div>
        <leftbar></leftbar>
      </el-aside>

      <el-container class="main-container">
        <!-- 聊天头部 -->
        <div class="main-header">
          <div class="header-title">
            <i class="el-icon-chat-dot-round"></i>
            <span>Timer 智能助手</span>
          </div>
          <div class="header-actions">
            <div class="session-info" v-if="sessionId">
              <el-tooltip
                :content="'当前会话ID: ' + sessionId"
                placement="bottom"
              >
                <span class="session-badge"
                  ><i class="el-icon-connection"></i> 会话已连接</span
                >
              </el-tooltip>
            </div>
            <el-tooltip content="帮助" placement="bottom">
              <el-button type="text" icon="el-icon-question" circle></el-button>
            </el-tooltip>
            <el-tooltip content="设置" placement="bottom">
              <el-button type="text" icon="el-icon-setting" circle></el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- 聊天体部分 - 包含内容和输入框 -->
        <div class="chat-body">
          <!-- 聊天内容区域 -->
          <div class="chat-content">
            <div class="welcome-banner" v-if="messages.length <= 1">
              <img
                src="https://www.deepseek.com/favicon.ico"
                class="banner-logo"
              />
              <h2>Timer 智能助手</h2>
              <p>您的AI驱动日程管理专家，随时为您提供智能建议和帮助</p>
            </div>
            <ChattingBox :messages="messages" ref="chatBox"></ChattingBox>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <div class="input-container">
              <el-input
                v-model="userinput"
                class="chat-input"
                :autosize="{ minRows: 1, maxRows: 4 }"
                type="textarea"
                placeholder="输入您的问题..."
                @keyup.enter.ctrl="sendmessage"
              />
              <div class="input-actions">
                <el-tooltip content="清空对话" placement="top">
                  <el-button
                    type="text"
                    icon="el-icon-delete"
                    @click="cleanmessage"
                    class="action-btn"
                  ></el-button>
                </el-tooltip>
                <el-button
                  type="primary"
                  @click="sendmessage"
                  icon="el-icon-s-promotion"
                  class="send-btn"
                  >发送</el-button
                >
              </div>
            </div>
            <div class="chat-tips">提示：按 Ctrl + Enter 快捷发送</div>
          </div>
        </div>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import ChattingBox from "../components/ChattingBox.vue";
import { cloneDeep } from "lodash";
export default {
  components: {
    ChattingBox,
  },
  data() {
    return {
      messages: [
        { text: "你好！", align: "left" },
        { text: "你好！", align: "right" },
        { text: "功能开发中... ...", align: "left" },
      ],
      userinput: "",
      sessionId: null, // 存储会话ID
    };
  },
  mounted() {
    // 初始欢迎消息
    this.messages = [
      {
        text: "你好！我是Timer智能助手，有什么我可以帮助你的吗？",
        align: "left",
      },
    ];

    // 尝试从localStorage获取保存的会话ID，如果没有则生成一个新的
    this.sessionId = localStorage.getItem("chat_session_id");
    if (!this.sessionId) {
      // 生成一个随机的会话ID
      this.sessionId = this.generateSessionId();
      localStorage.setItem("chat_session_id", this.sessionId);
    }
    console.log("当前会话ID:", this.sessionId);
  },
  updated() {
    // 每次更新后滚动到底部
    this.scrollToBottom();
  },
  methods: {
    async sendmessage() {
      if (this.userinput == "") return;
      // 处理Ctrl+Enter发送，但不添加额外的换行符
      if (event && event.ctrlKey && event.key === "Enter") {
        event.preventDefault();
      }

      let addms = cloneDeep(this.userinput);
      this.userinput = "";
      this.messages.push({ text: addms, align: "right" });
      this.scrollToBottom();

      try {
        // 显示加载状态
        this.messages.push({
          text: "正在思考中...",
          align: "left",
          loading: true,
        });
        this.scrollToBottom();

        // 准备请求数据
        const requestData = {
          message: addms,
          // 始终添加会话ID到请求中
          session_id: this.sessionId,
        };

        // 发送请求到后端API
        const response = await fetch("http://127.0.0.1:5000/chat/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
          credentials: "include", // 仍然包含cookie作为备选
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        // 移除加载状态消息
        this.messages.pop();

        // 添加AI回复
        this.messages.push({ text: data.response, align: "left" });

        // 保存会话ID
        if (data.session_id) {
          this.sessionId = data.session_id;
          localStorage.setItem("chat_session_id", data.session_id);
          console.log("保存会话ID:", data.session_id);
        }

        this.scrollToBottom();
      } catch (error) {
        console.error("Error:", error);
        // 移除加载状态消息
        this.messages.pop();
        // 显示错误消息
        this.messages.push({
          text: "抱歉，连接服务器失败，请检查后端是否正常运行。",
          align: "left",
        });
        this.scrollToBottom();
      }
    },
    cleanmessage() {
      this.$confirm("确定要清空所有对话记录吗? 这将重置当前会话。", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          // 清空消息
          this.messages = [
            {
              text: "对话已清空，有什么我可以帮助你的吗？",
              align: "left",
            },
          ];

          // 清除会话ID
          this.sessionId = null;
          localStorage.removeItem("chat_session_id");

          this.$message({
            type: "success",
            message: "对话记录已清空，会话已重置",
          });
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消清空操作",
          });
        });
    },
    scrollToBottom() {
      // 确保DOM更新后再滚动
      this.$nextTick(() => {
        const chatBox = this.$refs.chatBox.$el;
        if (chatBox) {
          chatBox.scrollTop = chatBox.scrollHeight;
        }
      });
    },

    // 生成一个随机的会话ID
    generateSessionId() {
      // 生成一个随机字符串作为会话ID
      const randomPart = Math.random().toString(36).substring(2, 15);
      const timestamp = new Date().getTime().toString(36);
      return `timer_${timestamp}_${randomPart}`;
    },
  },
};
</script>

<style scoped>
.chat-page {
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: #f8fbff;
  color: #333;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

/* 侧边栏样式 */
.sidebar {
  background-color: #f0f5ff;
  color: #333;
  box-shadow: 0 0 15px rgba(24, 144, 255, 0.08);
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e6f0ff;
  transition: all 0.3s;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #e6f0ff;
  margin-bottom: 12px;
  background: linear-gradient(to right, #e6f0ff, #f0f5ff);
}

.app-logo {
  display: flex;
  align-items: center;
  color: #1890ff;
}

.app-logo img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
  filter: drop-shadow(0 2px 4px rgba(24, 144, 255, 0.2));
}

.app-logo h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  background: linear-gradient(45deg, #1890ff, #69c0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 主容器样式 */
.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  max-height: 100vh; /* 限制最大高度 */
}

/* 聊天体部分样式 */
.chat-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  position: relative;
  height: calc(100vh - 64px); /* 减去头部高度 */
}

/* 头部样式 */
.main-header {
  background-color: #fff;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
  z-index: 10;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.header-title i {
  margin-right: 8px;
  font-size: 20px;
  color: #1890ff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-info {
  margin-right: 10px;
}

.session-badge {
  display: flex;
  align-items: center;
  background-color: #e6f7ff;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid #91d5ff;
  cursor: default;
}

.session-badge i {
  margin-right: 4px;
  font-size: 14px;
}

/* 欢迎横幅 */
.welcome-banner {
  text-align: center;
  padding: 40px 20px;
  margin: 20px auto;
  max-width: 600px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.08);
  border: 1px solid #e6f0ff;
}

.banner-logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.welcome-banner h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.welcome-banner p {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
}

/* 聊天内容区域 */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #ffffff;
  scrollbar-width: thin;
  scrollbar-color: #a0c8ff #f0f5ff;
  min-height: 0; /* 防止内容溢出 */
}

.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: #f0f5ff;
}

.chat-content::-webkit-scrollbar-thumb {
  background-color: #a0c8ff;
  border-radius: 3px;
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 24px;
  background-color: #ffffff;
  border-top: 1px solid #f0f0f0;
  position: relative;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 8px;
  width: 100%;
}

.chat-input {
  flex: 1;
  border-radius: 8px;
}

.chat-input >>> .el-textarea__inner {
  border-color: #e8e8e8;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
  transition: all 0.3s;
}

.chat-input >>> .el-textarea__inner:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  color: #999;
  transition: all 0.3s;
}

.action-btn:hover {
  color: #f56c6c;
}

.send-btn {
  padding: 8px 16px;
  border-radius: 6px;
  background-color: #1890ff;
  border-color: #1890ff;
  transition: all 0.3s;
}

.send-btn:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

.chat-tips {
  font-size: 12px;
  color: #999;
  text-align: right;
}
</style>
