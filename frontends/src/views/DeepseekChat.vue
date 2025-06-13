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
import axios from "axios";

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
      schedules: [], // 存储用户日程
    };
  },
  mounted() {
    // 初始欢迎消息
    this.messages = [
      {
        text: "你好！我是Timer智能助手，有什么我可以帮助你的吗？我可以帮你查看和管理日程。",
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

    // 获取用户日程
    this.fetchSchedules();
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

      // 检查是否包含日程关键词，如果有则尝试处理日程相关命令
      if (this.isScheduleRelatedQuery(addms)) {
        await this.handleScheduleQuery(addms);
        return;
      }

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
        const response = await fetch("/chat/", {
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
    // 判断是否是日程相关的查询
    isScheduleRelatedQuery(query) {
      const keywords = [
        "日程",
        "安排",
        "计划",
        "行程",
        "日历",
        "提醒",
        "待办",
        "schedule",
        "appointment",
      ];
      return keywords.some((keyword) => query.toLowerCase().includes(keyword));
    },

    // 处理日程相关的查询
    async handleScheduleQuery(query) {
      try {
        // 重新获取最新日程
        await this.fetchSchedules();

        if (
          query.includes("查看") ||
          query.includes("显示") ||
          query.includes("列出") ||
          query.includes("我的日程")
        ) {
          this.showSchedules();
        } else if (query.includes("今天") || query.includes("today")) {
          this.showTodaySchedules();
        } else if (query.includes("明天") || query.includes("tomorrow")) {
          this.showTomorrowSchedules();
        } else if (
          query.includes("本周") ||
          query.includes("这周") ||
          query.includes("week")
        ) {
          this.showWeekSchedules();
        } else {
          // 如果不是特定命令，则转给AI处理
          this.messages.push({
            text: "正在思考中...",
            align: "left",
            loading: true,
          });
          this.scrollToBottom();

          // 准备请求数据
          const requestData = {
            message: query,
            session_id: this.sessionId,
          };

          // 发送请求到后端API
          const response = await fetch("/chat/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
            credentials: "include",
          });

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const data = await response.json();

          // 移除加载状态消息
          this.messages.pop();

          // 添加AI回复
          this.messages.push({ text: data.response, align: "left" });
        }
      } catch (error) {
        console.error("处理日程查询失败:", error);
        this.messages.push({
          text: "抱歉，处理日程查询时出错，请稍后再试。",
          align: "left",
        });
      }
    },

    // 获取所有日程
    async fetchSchedules() {
      try {
        const response = await axios.get("/schedule/");
        this.schedules = response.data.schedules;
      } catch (error) {
        console.error("获取日程失败:", error);
        this.messages.push({
          text: "抱歉，获取日程失败，请检查网络连接。",
          align: "left",
        });
      }
    },

    // 显示所有日程
    showSchedules() {
      if (this.schedules.length === 0) {
        this.messages.push({
          text: "您目前没有任何日程安排。",
          align: "left",
        });
        return;
      }

      let scheduleText = "以下是您的所有日程安排：\n\n";
      this.schedules.forEach((schedule, index) => {
        scheduleText += `${index + 1}. ${schedule.title}\n`;
        scheduleText += `   开始时间: ${this.formatDateTime(
          schedule.start_time
        )}\n`;
        scheduleText += `   结束时间: ${this.formatDateTime(
          schedule.end_time
        )}\n`;
        scheduleText += `   状态: ${this.getStatusText(schedule.status)}\n\n`;
      });

      this.messages.push({
        text: scheduleText,
        align: "left",
      });
    },

    // 显示今天的日程
    showTodaySchedules() {
      const today = new Date().toISOString().split("T")[0];
      const todaySchedules = this.schedules.filter((schedule) => {
        const scheduleStartDate = new Date(schedule.start_time)
          .toISOString()
          .split("T")[0];
        return scheduleStartDate === today;
      });

      if (todaySchedules.length === 0) {
        this.messages.push({
          text: "今天没有日程安排。",
          align: "left",
        });
        return;
      }

      let scheduleText = "以下是今天的日程安排：\n\n";
      todaySchedules.forEach((schedule, index) => {
        scheduleText += `${index + 1}. ${schedule.title}\n`;
        scheduleText += `   开始时间: ${this.formatDateTime(
          schedule.start_time
        )}\n`;
        scheduleText += `   结束时间: ${this.formatDateTime(
          schedule.end_time
        )}\n`;
        scheduleText += `   状态: ${this.getStatusText(schedule.status)}\n\n`;
      });

      this.messages.push({
        text: scheduleText,
        align: "left",
      });
    },

    // 显示明天的日程
    showTomorrowSchedules() {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split("T")[0];

      const tomorrowSchedules = this.schedules.filter((schedule) => {
        const scheduleStartDate = new Date(schedule.start_time)
          .toISOString()
          .split("T")[0];
        return scheduleStartDate === tomorrowStr;
      });

      if (tomorrowSchedules.length === 0) {
        this.messages.push({
          text: "明天没有日程安排。",
          align: "left",
        });
        return;
      }

      let scheduleText = "以下是明天的日程安排：\n\n";
      tomorrowSchedules.forEach((schedule, index) => {
        scheduleText += `${index + 1}. ${schedule.title}\n`;
        scheduleText += `   开始时间: ${this.formatDateTime(
          schedule.start_time
        )}\n`;
        scheduleText += `   结束时间: ${this.formatDateTime(
          schedule.end_time
        )}\n`;
        scheduleText += `   状态: ${this.getStatusText(schedule.status)}\n\n`;
      });

      this.messages.push({
        text: scheduleText,
        align: "left",
      });
    },

    // 显示本周的日程
    showWeekSchedules() {
      const today = new Date();
      const firstDay = new Date(today);
      const lastDay = new Date(today);

      // 设置为本周的第一天（周日）
      const dayOfWeek = today.getDay();
      firstDay.setDate(today.getDate() - dayOfWeek);

      // 设置为本周的最后一天（周六）
      lastDay.setDate(firstDay.getDate() + 6);

      const firstDayStr = firstDay.toISOString().split("T")[0];
      const lastDayStr = lastDay.toISOString().split("T")[0];

      const weekSchedules = this.schedules.filter((schedule) => {
        const scheduleDate = new Date(schedule.start_time)
          .toISOString()
          .split("T")[0];
        return scheduleDate >= firstDayStr && scheduleDate <= lastDayStr;
      });

      if (weekSchedules.length === 0) {
        this.messages.push({
          text: "本周没有日程安排。",
          align: "left",
        });
        return;
      }

      let scheduleText = `以下是本周(${this.formatDate(
        firstDay
      )} 至 ${this.formatDate(lastDay)})的日程安排：\n\n`;

      // 按日期分组
      const groupedSchedules = {};
      weekSchedules.forEach((schedule) => {
        const dateStr = new Date(schedule.start_time)
          .toISOString()
          .split("T")[0];
        if (!groupedSchedules[dateStr]) {
          groupedSchedules[dateStr] = [];
        }
        groupedSchedules[dateStr].push(schedule);
      });

      // 按日期顺序显示
      Object.keys(groupedSchedules)
        .sort()
        .forEach((dateStr) => {
          const date = new Date(dateStr);
          scheduleText += `【${this.formatDate(date)} ${this.getWeekdayName(
            date.getDay()
          )}】\n`;

          groupedSchedules[dateStr].forEach((schedule, index) => {
            scheduleText += `${index + 1}. ${schedule.title}\n`;
            scheduleText += `   开始时间: ${this.formatDateTime(
              schedule.start_time
            )}\n`;
            scheduleText += `   结束时间: ${this.formatDateTime(
              schedule.end_time
            )}\n`;
            scheduleText += `   状态: ${this.getStatusText(
              schedule.status
            )}\n\n`;
          });
        });

      this.messages.push({
        text: scheduleText,
        align: "left",
      });
    },

    // 格式化日期
    formatDate(date) {
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}-${String(date.getDate()).padStart(2, "0")}`;
    },

    // 格式化日期时间
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return "未设置";
      const date = new Date(dateTimeStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}-${String(date.getDate()).padStart(2, "0")} ${String(
        date.getHours()
      ).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    },

    // 获取星期几
    getWeekdayName(day) {
      const weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
      return weekdays[day];
    },

    // 获取状态文本
    getStatusText(status) {
      switch (status) {
        case "waiting":
          return "等待中";
        case "running":
          return "进行中";
        case "finished":
          return "已完成";
        case "archived":
          return "已归档";
        default:
          return "未知状态";
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
