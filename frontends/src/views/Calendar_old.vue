<template>
  <div class="calendar">
    <el-container>
      <el-aside width="200px">
        <leftbar></leftbar>
      </el-aside>
      <el-container style="background-color: #eeeeee; padding: 20px">
        <div class="custom-calendar">
          <div class="calendar-header">
            <el-button
              type="primary"
              @click="prevMonth"
              icon="el-icon-arrow-left"
              >上个月</el-button
            >
            <h2>{{ currentYear }}年 {{ currentMonth }}月</h2>
            <el-button
              type="primary"
              @click="nextMonth"
              icon="el-icon-arrow-right"
              >下个月</el-button
            >
            <el-button type="success" @click="openCreateDialog"
              >创建日程</el-button
            >
          </div>

          <div class="weekdays">
            <div v-for="day in weekdays" :key="day" class="weekday">
              {{ day }}
            </div>
          </div>

          <div class="days">
            <div
              v-for="(day, index) in days"
              :key="index"
              :class="[
                'day',
                { 'current-month': day.currentMonth },
                { today: day.isToday },
              ]"
              @click="selectDate(day)"
            >
              <div class="day-number">{{ day.day }}</div>

              <!-- 显示日程 -->
              <div
                v-if="day.schedules && day.schedules.length > 0"
                class="schedule-container"
              >
                <div
                  v-for="schedule in day.schedules"
                  :key="schedule.id"
                  class="schedule-item"
                  :style="{
                    backgroundColor: getScheduleColor(schedule.status),
                  }"
                  @click.stop="viewSchedule(schedule)"
                >
                  {{ schedule.title }}
                </div>
              </div>

              <!-- 显示日程数量提示 -->
              <div
                v-if="day.schedules && day.schedules.length > 0"
                class="schedule-count"
              >
                {{ day.schedules.length }}个日程
              </div>
            </div>
          </div>
        </div>
      </el-container>
    </el-container>

    <!-- 查看日程的对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="selectedSchedule ? selectedSchedule.title : '日程详情'"
      width="50%"
    >
      <div v-if="selectedSchedule" class="schedule-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="标题">{{
            selectedSchedule.title
          }}</el-descriptions-item>
          <el-descriptions-item label="内容">{{
            selectedSchedule.description
          }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{
            selectedSchedule.start_time
          }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{
            selectedSchedule.end_time
          }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedSchedule.status)">{{
              getStatusText(selectedSchedule.status)
            }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提前提醒"
            >{{ selectedSchedule.remind_before }}分钟</el-descriptions-item
          >
          <el-descriptions-item label="创建时间">{{
            selectedSchedule.timestamp
          }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="openEditDialog">编辑</el-button>
          <el-button type="danger" @click="confirmDelete">删除</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建/编辑日程的对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEditing ? '编辑日程' : '创建日程'"
      width="50%"
    >
      <el-form :model="scheduleForm" label-width="80px">
        <el-form-item label="标题">
          <el-input
            v-model="scheduleForm.title"
            placeholder="请输入日程标题"
          ></el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="scheduleForm.description"
            type="textarea"
            placeholder="请输入日程内容"
          ></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="scheduleForm.status" placeholder="请选择日程状态">
            <el-option label="等待中" value="waiting"></el-option>
            <el-option label="进行中" value="running"></el-option>
            <el-option label="已完成" value="finished"></el-option>
            <el-option label="已归档" value="archived"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="scheduleForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="scheduleForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="提前提醒">
          <div class="remind-before-container">
            <el-input-number
              v-model="scheduleForm.remind_before"
              :min="0"
              :max="60"
              controls-position="right"
            ></el-input-number>
            <span class="remind-unit">分钟</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSchedule">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="删除日程" width="30%">
      <p>确定要删除这个日程吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteSchedule">确定删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

// 一周的日期
const weekdays = ["日", "一", "二", "三", "四", "五", "六"];

// 日历状态
const currentDate = ref(new Date());
const currentYear = ref(currentDate.value.getFullYear());
const currentMonth = ref(currentDate.value.getMonth() + 1);

// 日程数据
const schedules = ref([]);
const viewDialogVisible = ref(false);
const editDialogVisible = ref(false);
const deleteDialogVisible = ref(false);
const selectedSchedule = ref(null);
const selectedDate = ref(null);
const isEditing = ref(false);

// 日程表单
const scheduleForm = ref({
  id: null,
  title: "",
  description: "",
  status: "waiting",
  start_time: null,
  end_time: null,
  remind_before: 15,
});

// 获取所有日程数据
const fetchSchedules = async () => {
  try {
    const response = await axios.get("/schedule/");
    schedules.value = response.data.schedules;

    // console.log("获取到的日程数据:", schedules.value);

    // 检查日程数据结构，特别是ID字段
    if (schedules.value && schedules.value.length > 0) {
      const firstSchedule = schedules.value[0];
      // console.log("日程数据结构:", Object.keys(firstSchedule));
      // console.log("ID字段值:", firstSchedule.id);
      // console.log("ID字段类型:", typeof firstSchedule.id);
    }
  } catch (error) {
    console.error("获取日程数据失败:", error);
    // 显示错误消息
    ElMessage.error("获取日程数据失败");
  }
};

// 解析日期时间字符串为Date对象
const parseDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null;
  // 格式: "2025-06-12 00:00:00"
  const [datePart, timePart] = dateTimeStr.split(" ");
  const [year, month, day] = datePart.split("-").map(Number);
  const [hours, minutes, seconds] = timePart
    ? timePart.split(":").map(Number)
    : [0, 0, 0];

  return new Date(year, month - 1, day, hours, minutes, seconds);
};

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return "";

  // 如果是数字（时间戳），转换为字符串
  if (typeof dateTimeStr === "number") {
    const date = new Date(dateTimeStr * 1000);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
      2,
      "0"
    )}-${String(date.getDate()).padStart(2, "0")} ${String(
      date.getHours()
    ).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  }

  // 如果已经是字符串格式，直接返回
  return dateTimeStr;
};

// 获取指定日期的日程
const getSchedulesForDay = (year, month, day) => {
  if (!schedules.value || schedules.value.length === 0) return [];

  const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(
    day
  ).padStart(2, "0")}`;

  return schedules.value.filter((schedule) => {
    // 处理后端返回的日期时间字符串格式 "2025-06-12 00:00:00"
    if (schedule.start_time && typeof schedule.start_time === "string") {
      const startDateStr = schedule.start_time.split(" ")[0]; // 只取日期部分
      return startDateStr === dateStr;
    }
    return false;
  });
};

// 获取日程颜色
const getScheduleColor = (type) => {
  const colors = {
    work: "#67C23A",
    meeting: "#409EFF",
    personal: "#E6A23C",
    other: "#909399",
    waiting: "#E6A23C",
    running: "#67C23A",
    finished: "#909399",
    archived: "#909399",
  };

  return colors[type] || "#909399";
};

// 选择日期
const selectDate = (day) => {
  selectedDate.value = day;
  // 打开创建日程对话框
  openCreateDialog();
};

// 生成随机ID的函数
const generateRandomId = () => {
  // 生成一个10位数的随机ID
  return Math.floor(Math.random() * 9000000000) + 1000000000;
};

// 打开创建日程对话框
const openCreateDialog = () => {
  isEditing.value = false;

  // 重置表单，并生成一个随机ID
  scheduleForm.value = {
    id: generateRandomId(), // 生成随机ID
    title: "",
    description: "",
    status: "waiting",
    start_time: null,
    end_time: null,
    remind_before: 15,
  };

  // 如果有选择日期，设置默认开始和结束时间
  if (selectedDate.value) {
    const [year, month, day] = selectedDate.value.date.split("-").map(Number);
    const startDate = new Date(year, month - 1, day, 9, 0); // 默认上午9点
    const endDate = new Date(year, month - 1, day, 10, 0); // 默认10点结束

    scheduleForm.value.start_time = startDate;
    scheduleForm.value.end_time = endDate;
  }

  editDialogVisible.value = true;
};

// 查看日程详情
const viewSchedule = (schedule) => {
  // console.log("查看日程:", schedule);
  // console.log("日程ID:", schedule.id);
  // console.log("日程ID类型:", typeof schedule.id);

  selectedSchedule.value = { ...schedule }; // 使用解构赋值创建新对象
  // console.log("选中的日程:", selectedSchedule.value);
  viewDialogVisible.value = true;
};

// 打开编辑日程对话框
const openEditDialog = () => {
  if (!selectedSchedule.value) return;

  isEditing.value = true;

  // 填充表单，确保id正确传递
  scheduleForm.value = {
    id: selectedSchedule.value.id,
    title: selectedSchedule.value.title || "",
    description: selectedSchedule.value.description || "",
    status: selectedSchedule.value.status || "waiting",
    start_time: selectedSchedule.value.start_time
      ? parseDateTime(selectedSchedule.value.start_time)
      : null,
    end_time: selectedSchedule.value.end_time
      ? parseDateTime(selectedSchedule.value.end_time)
      : null,
    remind_before: selectedSchedule.value.remind_before || 15,
  };

  // console.log("编辑日程ID:", scheduleForm.value.id); // 添加日志，检查ID是否正确

  viewDialogVisible.value = false;
  editDialogVisible.value = true;
};

// 保存日程
const saveSchedule = async () => {
  // 验证表单
  if (!scheduleForm.value.title) {
    ElMessage.warning("请输入日程标题");
    return;
  }

  if (!scheduleForm.value.start_time) {
    ElMessage.warning("请选择开始时间");
    return;
  }

  if (!scheduleForm.value.end_time) {
    ElMessage.warning("请选择结束时间");
    return;
  }

  try {
    // 格式化日期为字符串格式
    const formatDate = (date) => {
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}-${String(date.getDate()).padStart(2, "0")} ${String(
        date.getHours()
      ).padStart(2, "0")}:${String(date.getMinutes()).padStart(
        2,
        "0"
      )}:${String(date.getSeconds()).padStart(2, "0")}`;
    };

    // const formData = {
    //   ...scheduleForm.value,
    //   start_time: formatDate(scheduleForm.value.start_time),
    //   end_time: formatDate(scheduleForm.value.end_time),
    //   timestamp: formatDate(new Date()),
    // };

    const formDataUPT = {
      id : scheduleForm.value.id,
      type : "schedule",
      content : {
        title : scheduleForm.value.title,
        content : scheduleForm.value.description,
        begin_time : formatDate(scheduleForm.value.start_time),
        end_time : formatDate(scheduleForm.value.end_time),
      }
      // start_time: formatDate(scheduleForm.value.start_time),
      // end_time: formatDate(scheduleForm.value.end_time),
    };

    let response;

    if (isEditing.value) {
      // 编辑现有日程
      if (!formDataUPT.id) {
        ElMessage.error("日程ID不能为空");
        return;
      }

      // console.log("提交编辑日程:", formDataUPT); // 添加日志，检查提交的数据

      response = await axios.put(`/schedule/${formDataUPT.id}`, {
        schedule: formDataUPT,
      });

      if (response.data.success) {
        ElMessage.success("日程更新成功");
      } else {
        ElMessage.error("日程更新失败");
        return;
      }
    } else {
      // 创建新日程
      // console.log("提交新建日程:", formDataUPT); // 添加日志，检查提交的数据

      response = await axios.post("/schedule/", {
        schedules: [formDataUPT],
      });

      if (response.data.ids && response.data.ids.length > 0) {
        ElMessage.success("日程创建成功");
      } else {
        ElMessage.error("日程创建失败");
        return;
      }
    }

    // 关闭对话框
    editDialogVisible.value = false;

    // 重新获取日程数据
    await fetchSchedules();
  } catch (error) {
    console.error("保存日程失败:", error);
    ElMessage.error("保存日程失败");
  }
};

// 确认删除
const confirmDelete = () => {
  if (!selectedSchedule.value) return;
  viewDialogVisible.value = false;
  deleteDialogVisible.value = true;
};

// 删除日程
const deleteSchedule = async () => {
  if (!selectedSchedule.value) return;

  try {
    const response = await axios.delete(
      `/schedule/${selectedSchedule.value.id}`
    );

    if (response.data.success) {
      ElMessage.success("日程删除成功");
      deleteDialogVisible.value = false;

      // 重新获取日程数据
      await fetchSchedules();
    } else {
      ElMessage.error("日程删除失败");
    }
  } catch (error) {
    console.error("删除日程失败:", error);
    ElMessage.error("删除日程失败");
  }
};

// 获取当月的天数
const getDaysInMonth = (year, month) => {
  return new Date(year, month, 0).getDate();
};

// 获取当月第一天是星期几
const getFirstDayOfMonth = (year, month) => {
  return new Date(year, month - 1, 1).getDay();
};

// 计算日历中显示的所有日期
const days = computed(() => {
  const result = [];
  const daysInMonth = getDaysInMonth(currentYear.value, currentMonth.value);
  const firstDayOfMonth = getFirstDayOfMonth(
    currentYear.value,
    currentMonth.value
  );

  // 上个月的日期
  const prevMonthDays = getDaysInMonth(
    currentMonth.value === 1 ? currentYear.value - 1 : currentYear.value,
    currentMonth.value === 1 ? 12 : currentMonth.value - 1
  );

  for (let i = firstDayOfMonth - 1; i >= 0; i--) {
    const day = prevMonthDays - i;
    const year =
      currentMonth.value === 1 ? currentYear.value - 1 : currentYear.value;
    const month = currentMonth.value === 1 ? 12 : currentMonth.value - 1;

    result.push({
      day,
      currentMonth: false,
      isToday: false,
      date: `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(
        2,
        "0"
      )}`,
      schedules: getSchedulesForDay(year, month, day),
    });
  }

  // 当月的日期
  const today = new Date();
  const todayDate = today.getDate();
  const todayMonth = today.getMonth() + 1;
  const todayYear = today.getFullYear();

  for (let i = 1; i <= daysInMonth; i++) {
    result.push({
      day: i,
      currentMonth: true,
      isToday:
        i === todayDate &&
        currentMonth.value === todayMonth &&
        currentYear.value === todayYear,
      date: `${currentYear.value}-${String(currentMonth.value).padStart(
        2,
        "0"
      )}-${String(i).padStart(2, "0")}`,
      schedules: getSchedulesForDay(currentYear.value, currentMonth.value, i),
    });
  }

  // 下个月的日期
  const totalDaysDisplayed = Math.ceil((firstDayOfMonth + daysInMonth) / 7) * 7;
  const nextMonthDays = totalDaysDisplayed - (firstDayOfMonth + daysInMonth);

  for (let i = 1; i <= nextMonthDays; i++) {
    const year =
      currentMonth.value === 12 ? currentYear.value + 1 : currentYear.value;
    const month = currentMonth.value === 12 ? 1 : currentMonth.value + 1;

    result.push({
      day: i,
      currentMonth: false,
      isToday: false,
      date: `${year}-${String(month).padStart(2, "0")}-${String(i).padStart(
        2,
        "0"
      )}`,
      schedules: getSchedulesForDay(year, month, i),
    });
  }

  return result;
});

// 上个月
const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12;
    currentYear.value -= 1;
  } else {
    currentMonth.value -= 1;
  }
};

// 下个月
const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1;
    currentYear.value += 1;
  } else {
    currentMonth.value += 1;
  }
};

// 监听月份变化，重新获取日程
const fetchSchedulesOnMonthChange = () => {
  fetchSchedules();
};

// 监听切换月份
watch(
  () => [currentYear.value, currentMonth.value],
  fetchSchedulesOnMonthChange
);

// 组件挂载时获取日程数据
onMounted(() => {
  fetchSchedules();
});

// 获取状态类型（用于el-tag的type属性）
const getStatusType = (status) => {
  const types = {
    waiting: "warning",
    running: "success",
    finished: "info",
    archived: "info",
  };
  return types[status] || "info";
};

// 获取状态文本（中文显示）
const getStatusText = (status) => {
  const texts = {
    waiting: "等待中",
    running: "进行中",
    finished: "已完成",
    archived: "已归档",
  };
  return texts[status] || status;
};
</script>

<style scoped>
.custom-calendar {
  width: 100%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: white;
  border-radius: 4px;
  padding: 16px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-weight: bold;
  padding: 8px;
  background-color: #f5f7fa;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-gap: 1px;
  background-color: #ebeef5;
}

.day {
  background-color: white;
  padding: 10px;
  min-height: 120px;
  text-align: left;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.day:hover {
  background-color: #f5f7fa;
}

.day:not(.current-month) {
  color: #c0c4cc;
  background-color: #fafafa;
}

.day.today {
  background-color: #e6f7ff;
  border: 1px solid #1890ff;
}

.day-number {
  font-size: 14px;
  margin-bottom: 8px;
}

.schedule-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
  overflow-y: auto;
  max-height: 80px;
}

.schedule-item {
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 2px;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.schedule-item:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  transition: all 0.2s;
}

.schedule-count {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.remind-before-container {
  display: flex;
  align-items: center;
}

.remind-unit {
  margin-left: 8px;
}

.schedule-detail {
  padding: 10px;
}
</style>
