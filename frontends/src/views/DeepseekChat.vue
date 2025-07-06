<template>
  <div class="chat-page">
    <el-container>
      <el-aside width="240px" class="sidebar">
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
            <el-button
              type="text"
              icon="el-icon-delete"
              circle
              @click="cleanmessage"
            ></el-button>
            <el-button type="text" icon="el-icon-question" circle></el-button>
            <el-button type="text" icon="el-icon-setting" circle></el-button>
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
                <el-upload
                  class="upload-button"
                  action="#"
                  :show-file-list="false"
                  :before-upload="handleImageUpload"
                >
                  <el-button type="primary" size="small" plain class="ocr-btn"
                    >图片转文字</el-button
                  >
                </el-upload>
                <el-button
                  type="primary"
                  size="small"
                  plain
                  class="voice-btn"
                  @click="toggleVoiceRecording"
                  :class="{ recording: isRecording }"
                >
                  <i
                    :class="
                      isRecording ? 'el-icon-microphone' : 'el-icon-microphone'
                    "
                    class="mic-icon"
                  ></i>
                  {{ isRecording ? "结束录音" : "语音转文字" }}
                </el-button>
                <el-button type="primary" @click="sendmessage" class="send-btn"
                  >发送</el-button
                >
              </div>
            </div>
            <div class="chat-tips">提示：按 Ctrl + Enter 快捷发送</div>
          </div>
        </div>
      </el-container>
    </el-container>

    <!-- 图片识别加载弹窗 -->
    <el-dialog
      title="图片识别中"
      :visible.sync="ocrLoading"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="ocr-loading-content">
        <el-progress type="circle" :percentage="ocrProgress"></el-progress>
        <p>正在识别图片中的文字，请稍候...</p>
      </div>
    </el-dialog>

    <!-- 语音识别状态弹窗 -->
    <el-dialog
      title="语音识别中"
      :visible.sync="voiceRecording"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="voice-recording-content">
        <div class="voice-wave">
          <div
            v-for="i in 5"
            :key="i"
            class="voice-bar"
            :style="{ animationDelay: `${i * 0.1}s` }"
          ></div>
        </div>
        <p>正在录音，请说话... 录音时长: {{ recordingTime }}秒</p>
        <el-button type="danger" @click="stopVoiceRecording"
          >结束录音</el-button
        >
      </div>
    </el-dialog>
  </div>
</template>

<script>
import ChattingBox from "../components/ChattingBox.vue";
import { cloneDeep } from "lodash";
import axios from "axios";
import Tesseract from "tesseract.js";
import globalStore from "@/utils/GlobalStore";
import { SyncFromServer,PostDataToServer,GetDataFromServer,serverURL } from "@/utils/DataManager";

export default {
  components: {
    ChattingBox,
  },
  data() {
    return {
      messages: [
        { text: "你好！", align: "left" },
        { text: "你好！", align: "right" },
        // { text: "功能开发中... ...", align: "left" },
      ],
      userinput: "",
      sessionId: null, // 存储会话ID
      schedules: [], // 存储用户日程
      ocrLoading: false, // 图片识别加载状态
      ocrProgress: 0, // 图片识别进度
      isRecording: false, // 是否正在录音
      voiceRecording: false, // 语音录音弹窗状态
      recordingTime: 0, // 录音时长
      recordingTimer: null, // 录音计时器
      recognition: null, // 语音识别对象
    };
  },
  async mounted() {
    try {
      // 异步获取服务器数据
      const response = await GetDataFromServer(serverURL + "chat/remind");
      
      // 检查响应有效性
      if (response?.data?.response) {
        this.messages = [{
          text: response.data.response,
          align: "left"
        }];
      } else {
        throw new Error("无效的服务器响应");
      }
    } catch (error) {
      console.error("获取欢迎消息失败:", error);
      // 设置默认消息
      this.messages = [{
        text: "您好，欢迎使用系统！",
        align: "left"
      }];
    }

    // 尝试从localStorage获取保存的会话ID，如果没有则生成一个新的
    this.sessionId = localStorage.getItem("chat_session_id");
    if (!this.sessionId) {
      // 生成一个随机的会话ID
      this.sessionId = this.generateSessionId();
      localStorage.setItem("chat_session_id", this.sessionId);
    }
    // console.log("当前会话ID:", this.sessionId);

    // 获取用户日程
    this.fetchSchedules();

    // 初始化语音识别
    this.initSpeechRecognition();
  },
  updated() {
    // 每次更新后滚动到底部
    this.scrollToBottom();
  },
  methods: {
    // 初始化语音识别
    initSpeechRecognition() {
      // 检查浏览器是否支持语音识别
      if (
        "webkitSpeechRecognition" in window ||
        "SpeechRecognition" in window
      ) {
        const SpeechRecognition =
          window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // 设置语音识别参数
        this.recognition.continuous = true; // 持续识别
        this.recognition.interimResults = true; // 实时结果
        this.recognition.lang = "zh-CN"; // 设置中文识别

        // 处理识别结果
        this.recognition.onresult = (event) => {
          let finalTranscript = "";
          let interimTranscript = "";

          // 获取所有识别结果
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }

          // 更新输入框内容
          if (finalTranscript !== "") {
            if (this.userinput && this.userinput.trim() !== "") {
              this.userinput += " " + finalTranscript;
            } else {
              this.userinput = finalTranscript;
            }
          }
        };

        // 处理错误
        this.recognition.onerror = (event) => {
          console.error("语音识别错误:", event.error);
          this.stopVoiceRecording();
          this.$message.error(`语音识别错误: ${event.error}`);
        };

        // 处理结束
        this.recognition.onend = () => {
          // 如果仍处于录音状态，则继续录音（防止自动结束）
          if (this.isRecording) {
            this.recognition.start();
          } else {
            this.stopVoiceRecording();
          }
        };
      } else {
        console.warn("浏览器不支持语音识别");
      }
    },

    // 切换语音录音状态
    toggleVoiceRecording() {
      if (this.isRecording) {
        this.stopVoiceRecording();
      } else {
        this.startVoiceRecording();
      }
    },

    // 开始语音录音
    startVoiceRecording() {
      // 检查浏览器是否支持语音识别
      if (!this.recognition) {
        this.$message.warning("您的浏览器不支持语音识别功能");
        return;
      }

      try {
        // 开始录音
        this.recognition.start();
        this.isRecording = true;
        this.voiceRecording = true;
        this.recordingTime = 0;

        // 开始计时
        this.recordingTimer = setInterval(() => {
          this.recordingTime++;

          // 自动停止，如果超过1分钟
          if (this.recordingTime >= 60) {
            this.stopVoiceRecording();
            this.$message.info("录音已达到最大时长1分钟，已自动停止");
          }
        }, 1000);

        this.$message.success("开始录音，请说话...");
      } catch (error) {
        console.error("开始录音失败:", error);
        this.$message.error("开始录音失败，请重试");
        this.isRecording = false;
        this.voiceRecording = false;
      }
    },

    // 停止语音录音
    stopVoiceRecording() {
      if (this.recognition) {
        try {
          this.recognition.stop();
        } catch (error) {
          console.error("停止录音错误:", error);
        }
      }

      this.isRecording = false;
      this.voiceRecording = false;

      // 清除计时器
      if (this.recordingTimer) {
        clearInterval(this.recordingTimer);
        this.recordingTimer = null;
      }

      this.$message.success("录音已结束，内容已添加到输入框");
    },

    // 处理图片上传和识别（纯前端实现）
    async handleImageUpload(file) {
      // 检查文件类型
      if (!file.type.includes("image/")) {
        this.$message.error("请上传图片文件");
        return false;
      }

      this.ocrLoading = true;
      this.ocrProgress = 0;

      try {
        // 读取文件为URL
        const fileUrl = URL.createObjectURL(file);

        // 使用Tesseract.js识别图片文字
        const result = await Tesseract.recognize(
          fileUrl,
          "chi_sim", // 使用中文简体识别模型
          {
            logger: (progress) => {
              // 根据进度状态更新进度条
              if (progress.status === "recognizing text") {
                this.ocrProgress = Math.round(progress.progress * 100);
              } else if (progress.status === "loading language traineddata") {
                this.ocrProgress = 30;
              } else if (progress.status === "initializing api") {
                this.ocrProgress = 10;
              } else {
                // 其他阶段的进度
                if (this.ocrProgress < 30) {
                  this.ocrProgress = 30;
                }
              }
            },
          }
        );

        this.ocrProgress = 100;

        // 获取识别文本
        const recognizedText = result.data.text;

        // 如果成功，将识别的文本添加到输入框
        if (recognizedText && recognizedText.trim() !== "") {
          // 如果输入框已有内容，则添加换行符
          if (this.userinput && this.userinput.trim() !== "") {
            this.userinput += "\n" + recognizedText;
          } else {
            this.userinput = recognizedText;
          }
          this.$message.success("图片文字识别成功");
        } else {
          this.$message.warning("未能从图片中识别出文字");
        }

        // 释放URL对象
        URL.revokeObjectURL(fileUrl);

        setTimeout(() => {
          this.ocrLoading = false;
        }, 500);
      } catch (error) {
        console.error("图片识别失败:", error);
        this.$message.error("图片识别失败，请重试");
        this.ocrLoading = false;
      }

      // 阻止默认上传行为
      return false;
    },

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
      // if (this.isScheduleRelatedQuery(addms)) {
      //   await this.handleScheduleQuery(addms);
      //   return;
      // }

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
        // const queryP = new URLSearchParams({user_id:globalStore.UserID}).toString();

        // const response = await fetch("/chat?"+queryP, {
        //   method: "POST",
        //   headers: {
        //     "Content-Type": "application/json",
        //   },
        //   body: JSON.stringify({...requestData,user_id:globalStore.UserID}),
        //   credentials: "include", // 仍然包含cookie作为备选
        // });
        const response = await PostDataToServer(serverURL+"chat/",requestData)

        // if (!response.ok) {
        //   throw new Error(`HTTP error! Status: ${response.status}`);
        // }

        const data = await response.data;

        // 移除加载状态消息
        this.messages.pop();

        // 添加AI回复
        // console.log(data);
        if (data.schedule==undefined)
          this.messages.push({ text: data.response, align: "left" });
        else this.messages.push({ text: data.response, align: "left", schedule: data.schedule });

        // 保存会话ID
        if (data.session_id) {
          this.sessionId = data.session_id;
          localStorage.setItem("chat_session_id", data.session_id);
          // console.log("保存会话ID:", data.session_id);
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
        await SyncFromServer()
        this.schedules = cloneDeep(globalStore.UserSchedules);
      } catch {
        // console.log("error!");
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
        scheduleText += `${index + 1}. ${schedule.content.title}\n`;
        scheduleText += `   开始时间: ${this.formatDateTime(
          schedule.content.begin_time
        )}\n`;
        scheduleText += `   结束时间: ${this.formatDateTime(
          schedule.content.end_time
        )}\n`;
        scheduleText += `   内容: ${schedule.content.content==""?"无":schedule.content.content}\n`;
        scheduleText += `   状态: ${this.getStatusText(schedule.status?"finished":"running")}\n\n`;
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
  color: #1890ff;
}

.upload-button {
  display: inline-block;
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

.voice-btn {
  transition: all 0.3s;
}

.voice-btn.recording {
  background-color: #ff4d4f;
  border-color: #ff4d4f;
  color: white;
}

.chat-tips {
  font-size: 12px;
  color: #999;
  text-align: right;
}

/* 图片识别加载弹窗样式 */
.ocr-loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ocr-loading-content p {
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

/* 语音识别状态弹窗样式 */
.voice-recording-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.voice-wave {
  display: flex;
  align-items: center;
  height: 40px;
  margin-bottom: 20px;
}

.voice-bar {
  display: inline-block;
  width: 5px;
  height: 20px;
  background-color: #1890ff;
  margin: 0 3px;
  border-radius: 2px;
  animation: voice-wave 1.2s ease-in-out infinite;
}

@keyframes voice-wave {
  0%,
  100% {
    height: 10px;
  }
  50% {
    height: 35px;
  }
}

.voice-bar:nth-child(1) {
  animation-delay: 0s;
}
.voice-bar:nth-child(2) {
  animation-delay: 0.2s;
}
.voice-bar:nth-child(3) {
  animation-delay: 0.4s;
}
.voice-bar:nth-child(4) {
  animation-delay: 0.6s;
}
.voice-bar:nth-child(5) {
  animation-delay: 0.8s;
}

.voice-recording-content p {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.mic-icon {
  margin-right: 8px;
  color: inherit;
}
</style>
