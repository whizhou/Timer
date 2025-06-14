<template>
  <div class="dashboard">
    <el-container>
      <el-aside width="200px">
        <leftbar></leftbar>
      </el-aside>
      <el-container style="background-color: #eeeeee; padding: 20px">
        <div class="dashboard-container">
          <!-- 顶部统计卡片 -->
          <div class="stats-cards">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stats-card task-card" shadow="hover">
                  <div class="card-content">
                    <div class="card-icon">
                      <i class="el-icon-document"></i>
                    </div>
                    <div class="card-data">
                      <div class="card-value">{{ totalTasks }}</div>
                      <div class="card-label">总日程数</div>
                    </div>
                  </div>
                  <div class="card-footer">
                    <span class="trend">
                      <i class="el-icon-top" v-if="taskTrend > 0"></i>
                      <i class="el-icon-bottom" v-else-if="taskTrend < 0"></i>
                      <span>{{ Math.abs(taskTrend) }}% 较上周</span>
                    </span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stats-card pending-card" shadow="hover">
                  <div class="card-content">
                    <div class="card-icon">
                      <i class="el-icon-time"></i>
                    </div>
                    <div class="card-data">
                      <div class="card-value">{{ pendingTasks }}</div>
                      <div class="card-label">待办日程</div>
                    </div>
                  </div>
                  <div class="card-footer">
                    <span class="today-due">今日到期: {{ todayDueTasks }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stats-card completed-card" shadow="hover">
                  <div class="card-content">
                    <div class="card-icon">
                      <i class="el-icon-check"></i>
                    </div>
                    <div class="card-data">
                      <div class="card-value">{{ completedTasks }}</div>
                      <div class="card-label">已完成日程</div>
                    </div>
                  </div>
                  <div class="card-footer">
                    <el-progress
                      :percentage="completionRate"
                      :color="customColors"
                      :format="format"
                      class="completion-progress"
                    >
                    </el-progress>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stats-card efficiency-card" shadow="hover">
                  <div class="card-content">
                    <div class="card-icon">
                      <i class="el-icon-data-line"></i>
                    </div>
                    <div class="card-data">
                      <div class="card-value">{{ efficiencyScore }}</div>
                      <div class="card-label">效率得分</div>
                    </div>
                  </div>
                  <div class="card-footer">
                    <div class="score-stars">
                      <i
                        class="el-icon-star-on"
                        v-for="n in Math.floor(efficiencyScore / 20)"
                        :key="n"
                      ></i>
                      <i
                        class="el-icon-star-off"
                        v-for="n in 5 - Math.floor(efficiencyScore / 20)"
                        :key="`off-${n}`"
                      ></i>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 中间部分 - 图表和日程列表 -->
          <div class="middle-section">
            <el-row :gutter="20">
              <el-col :span="16">
                <el-card class="chart-card" shadow="hover">
                  <div slot="header" class="chart-header">
                    <span>日程完成趋势</span>
                    <el-radio-group v-model="chartTimeRange" size="small">
                      <el-radio-button label="week">本周</el-radio-button>
                      <el-radio-button label="month">本月</el-radio-button>
                      <el-radio-button label="year">今年</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div class="chart-container">
                    <div ref="taskChart" class="task-chart"></div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="upcoming-card" shadow="hover">
                  <div slot="header" class="upcoming-header">
                    <span>近期日程</span>
                    <!-- <el-button type="text" @click="viewAllTasks"
                      >查看全部</el-button
                    > -->
                  </div>
                  <div class="upcoming-list">
                    <el-timeline>
                      <el-timeline-item
                        v-for="(task, index) in upcomingTasks"
                        :key="index"
                        :timestamp="formatTaskTime(task.start_time)"
                        :type="getTaskTypeIcon(task.status)"
                        :color="getTaskColor(task.status)"
                      >
                        <div class="timeline-task-item">
                          <div class="task-title">{{ task.title }}</div>
                          <div class="task-status">
                            {{ getTaskStatusText(task.status) }}
                          </div>
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 底部部分 - 分类统计和日历预览 -->
          <div class="bottom-section">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="category-card" shadow="hover">
                  <div slot="header" class="category-header">
                    <span>日程分类统计</span>
                  </div>
                  <div class="category-chart">
                    <div ref="categoryPieChart" class="pie-chart"></div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="calendar-preview-card" shadow="hover">
                  <div slot="header" class="calendar-header">
                    <span>日历预览</span>
                    <el-button type="text" @click="goToCalendar"
                      >查看日历</el-button
                    >
                  </div>
                  <div class="calendar-container">
                    <el-calendar
                      class="mini-calendar"
                      :range="[new Date(), getNextWeekDate()]"
                    >
                    </el-calendar>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-container>
    </el-container>

    <!-- 欢迎提示 -->
    <el-dialog
      title="欢迎使用 Timer 智能日程管理系统"
      :visible.sync="showWelcomeDialog"
      width="50%"
      :before-close="closeWelcomeDialog"
    >
      <div class="welcome-content">
        <img src="https://www.deepseek.com/favicon.ico" class="welcome-logo" />
        <h2>您好，欢迎使用 Timer 系统!</h2>
        <p>这是您的个人仪表盘，在这里您可以:</p>
        <ul>
          <li>查看日程统计数据和完成进度</li>
          <li>浏览近期日程安排</li>
          <li>分析日程分类情况</li>
          <li>检查日历预览</li>
        </ul>
        <p class="tip">提示: 使用左侧菜单可以快速导航到其他功能页面</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-checkbox v-model="dontShowAgain">不再显示</el-checkbox>
        <el-button type="primary" @click="closeWelcomeDialog"
          >开始使用</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from "echarts";
import axios from "axios";
import leftbar from "../components/LeftBar.vue";

export default {
  name: "Dashboard",
  components: {
    leftbar,
  },
  data() {
    return {
      // 统计数据
      totalTasks: 0,
      pendingTasks: 0,
      completedTasks: 0,
      todayDueTasks: 0,
      taskTrend: 12, // 假设比上周增长12%
      completionRate: 0,
      efficiencyScore: 85,

      // 图表数据
      chartTimeRange: "week",
      taskChart: null,
      categoryChart: null,

      // 近期日程
      upcomingTasks: [],

      // 欢迎对话框
      showWelcomeDialog: false,
      dontShowAgain: false,

      // 自定义颜色
      customColors: [
        { color: "#f56c6c", percentage: 20 },
        { color: "#e6a23c", percentage: 40 },
        { color: "#5cb87a", percentage: 60 },
        { color: "#1989fa", percentage: 80 },
        { color: "#6f7ad3", percentage: 100 },
      ],
    };
  },
  async mounted() {
    // 检查是否显示欢迎对话框
    if (!localStorage.getItem("dashboard_welcome_shown")) {
      this.showWelcomeDialog = true;
    }

    // 获取数据
    await this.fetchData();

    // 初始化图表
    this.initTaskChart();
    this.initCategoryChart();

    // 监听窗口大小变化，调整图表大小
    window.addEventListener("resize", this.resizeCharts);
  },
  beforeDestroy() {
    // 移除事件监听
    window.removeEventListener("resize", this.resizeCharts);

    // 销毁图表实例
    if (this.taskChart) {
      this.taskChart.dispose();
    }
    if (this.categoryChart) {
      this.categoryChart.dispose();
    }
  },
  watch: {
    chartTimeRange() {
      this.updateTaskChart();
    },
  },
  methods: {
    // 格式化进度条文本
    format(percentage) {
      return percentage + "%";
    },

    // 获取下周日期
    getNextWeekDate() {
      const date = new Date();
      date.setDate(date.getDate() + 7);
      return date;
    },

    // 获取数据
    async fetchData() {
      try {
        // 获取日程数据
        const response = await axios.get("/schedule/");
        const schedules = response.data.schedules || [];

        // 计算统计数据
        this.totalTasks = schedules.length;
        this.pendingTasks = schedules.filter(
          (s) => s.status === "waiting"
        ).length;
        this.completedTasks = schedules.filter(
          (s) => s.status === "finished"
        ).length;
        this.completionRate =
          this.totalTasks > 0
            ? Math.round((this.completedTasks / this.totalTasks) * 100)
            : 0;

        // 计算今日到期任务
        const today = new Date().toISOString().split("T")[0];
        this.todayDueTasks = schedules.filter((s) => {
          const taskDate = new Date(s.end_time).toISOString().split("T")[0];
          return taskDate === today && s.status !== "finished";
        }).length;

        // 获取近期日程
        this.upcomingTasks = schedules
          .filter((s) => s.status !== "finished" && s.status !== "archived")
          .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
          .slice(0, 5);
      } catch (error) {
        console.error("获取数据失败:", error);
        this.$message.error("获取数据失败，请刷新页面重试");
      }
    },

    // 初始化任务图表
    initTaskChart() {
      this.taskChart = echarts.init(this.$refs.taskChart);
      this.updateTaskChart();
    },

    // 更新任务图表
    updateTaskChart() {
      let xAxisData = [];
      let completedData = [];
      let pendingData = [];

      // 根据时间范围生成数据
      if (this.chartTimeRange === "week") {
        const days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
        const today = new Date().getDay();

        // 生成本周的数据
        for (let i = 0; i < 7; i++) {
          xAxisData.push(days[(today + i) % 7]);
          completedData.push(Math.floor(Math.random() * 10));
          pendingData.push(Math.floor(Math.random() * 8));
        }
      } else if (this.chartTimeRange === "month") {
        // 生成本月的数据
        const daysInMonth = new Date(
          new Date().getFullYear(),
          new Date().getMonth() + 1,
          0
        ).getDate();
        for (let i = 1; i <= daysInMonth; i++) {
          xAxisData.push(i + "日");
          completedData.push(Math.floor(Math.random() * 10));
          pendingData.push(Math.floor(Math.random() * 8));
        }
      } else {
        // 生成今年的数据
        const months = [
          "1月",
          "2月",
          "3月",
          "4月",
          "5月",
          "6月",
          "7月",
          "8月",
          "9月",
          "10月",
          "11月",
          "12月",
        ];
        for (let i = 0; i < 12; i++) {
          xAxisData.push(months[i]);
          completedData.push(Math.floor(Math.random() * 30));
          pendingData.push(Math.floor(Math.random() * 20));
        }
      }

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          data: ["已完成", "待处理"],
          right: 10,
          top: 0,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: xAxisData,
          axisLine: {
            lineStyle: {
              color: "#ddd",
            },
          },
        },
        yAxis: {
          type: "value",
          splitLine: {
            lineStyle: {
              color: "#eee",
            },
          },
        },
        series: [
          {
            name: "已完成",
            type: "bar",
            stack: "total",
            emphasis: {
              focus: "series",
            },
            data: completedData,
            itemStyle: {
              color: "#67C23A",
            },
          },
          {
            name: "待处理",
            type: "bar",
            stack: "total",
            emphasis: {
              focus: "series",
            },
            data: pendingData,
            itemStyle: {
              color: "#E6A23C",
            },
          },
        ],
      };

      this.taskChart.setOption(option);
    },

    // 初始化分类图表
    initCategoryChart() {
      this.categoryChart = echarts.init(this.$refs.categoryPieChart);

      // 模拟数据
      const option = {
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b}: {c} ({d}%)",
        },
        legend: {
          orient: "vertical",
          right: 10,
          top: "center",
          data: ["工作", "学习", "会议", "休闲", "其他"],
        },
        series: [
          {
            name: "日程分类",
            type: "pie",
            radius: ["50%", "70%"],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: "#fff",
              borderWidth: 2,
            },
            label: {
              show: false,
              position: "center",
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "18",
                fontWeight: "bold",
              },
            },
            labelLine: {
              show: false,
            },
            data: [
              { value: 35, name: "工作", itemStyle: { color: "#409EFF" } },
              { value: 20, name: "学习", itemStyle: { color: "#67C23A" } },
              { value: 15, name: "会议", itemStyle: { color: "#E6A23C" } },
              { value: 10, name: "休闲", itemStyle: { color: "#F56C6C" } },
              { value: 5, name: "其他", itemStyle: { color: "#909399" } },
            ],
          },
        ],
      };

      this.categoryChart.setOption(option);
    },

    // 调整图表大小
    resizeCharts() {
      if (this.taskChart) {
        this.taskChart.resize();
      }
      if (this.categoryChart) {
        this.categoryChart.resize();
      }
    },

    // 格式化任务时间
    formatTaskTime(time) {
      if (!time) return "未设置";
      const date = new Date(time);
      return `${date.getMonth() + 1}月${date.getDate()}日 ${date
        .getHours()
        .toString()
        .padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
    },

    // 获取任务类型图标
    getTaskTypeIcon(status) {
      switch (status) {
        case "waiting":
          return "warning";
        case "running":
          return "primary";
        case "finished":
          return "success";
        case "archived":
          return "info";
        default:
          return "";
      }
    },

    // 获取任务颜色
    getTaskColor(status) {
      switch (status) {
        case "waiting":
          return "#E6A23C";
        case "running":
          return "#409EFF";
        case "finished":
          return "#67C23A";
        case "archived":
          return "#909399";
        default:
          return "#909399";
      }
    },

    // 获取任务状态文本
    getTaskStatusText(status) {
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

    // 查看全部任务
    viewAllTasks() {
      this.$router.push("/");
    },

    // 跳转到日历页面
    goToCalendar() {
      this.$router.push("/calendar");
    },

    // 关闭欢迎对话框
    closeWelcomeDialog() {
      this.showWelcomeDialog = false;
      if (this.dontShowAgain) {
        localStorage.setItem("dashboard_welcome_shown", "true");
      }
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  background-color: #f8fbff;
  min-height: calc(100vh - 40px);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 统计卡片 */
.stats-cards {
  margin-bottom: 20px;
}

.stats-card {
  height: 140px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.task-card {
  border-left: 4px solid #409eff;
}

.pending-card {
  border-left: 4px solid #e6a23c;
}

.completed-card {
  border-left: 4px solid #67c23a;
}

.efficiency-card {
  border-left: 4px solid #909399;
}

.card-content {
  display: flex;
  align-items: center;
  height: 80px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: #409eff;
}

.pending-card .card-icon {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.completed-card .card-icon {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.efficiency-card .card-icon {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.card-data {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.card-label {
  font-size: 14px;
  color: #909399;
}

.card-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}

.trend {
  display: flex;
  align-items: center;
}

.trend i.el-icon-top {
  color: #67c23a;
  margin-right: 5px;
}

.trend i.el-icon-bottom {
  color: #f56c6c;
  margin-right: 5px;
}

.today-due {
  color: #e6a23c;
}

.completion-progress {
  margin-top: 5px;
}

.score-stars {
  color: #ffd700;
  font-size: 16px;
}

/* 中间部分 */
.middle-section {
  margin-bottom: 20px;
}

.chart-card,
.upcoming-card {
  height: 400px;
  border-radius: 8px;
  transition: all 0.3s;
}

.chart-card:hover,
.upcoming-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08) !important;
}

.chart-header,
.upcoming-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-container {
  height: 320px;
  padding: 10px;
}

.task-chart {
  width: 100%;
  height: 100%;
}

.upcoming-list {
  height: 320px;
  overflow-y: auto;
  padding: 10px;
}

.timeline-task-item {
  padding: 5px 0;
}

.task-title {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 5px;
}

.task-status {
  font-size: 12px;
  color: #909399;
}

/* 底部部分 */
.bottom-section {
  margin-bottom: 20px;
}

.category-card,
.calendar-preview-card {
  height: 380px;
  border-radius: 8px;
  transition: all 0.3s;
}

.category-card:hover,
.calendar-preview-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08) !important;
}

.category-header,
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.category-chart {
  height: 300px;
  padding: 10px;
}

.pie-chart {
  width: 100%;
  height: 100%;
}

.calendar-container {
  height: 300px;
  overflow-y: auto;
  padding: 10px;
}

.mini-calendar {
  height: 100%;
  --el-calendar-cell-width: 40px;
  font-size: 12px;
}

/* 欢迎对话框 */
.welcome-content {
  text-align: center;
  padding: 20px;
}

.welcome-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
}

.welcome-content h2 {
  color: #409eff;
  margin-bottom: 20px;
}

.welcome-content ul {
  text-align: left;
  margin: 20px auto;
  max-width: 80%;
  line-height: 1.8;
}

.tip {
  color: #e6a23c;
  margin-top: 20px;
  font-style: italic;
}
</style>
