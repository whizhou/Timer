<template>
  <div class="calendar">
    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <el-main>
          <!-- 颜色图例 -->
          <div class="legend">
            <div class="legend-item">
              <div class="color-box start-color"></div>
              <span>开始日程</span>
            </div>
            <div class="legend-item">
              <div class="color-box end-color"></div>
              <span>结束日程</span>
            </div>
            <div class="legend-item">
              <div class="color-box both-color"></div>
              <span>开始并结束</span>
            </div>
          </div>
          
          <div class="calendar-container">
            <el-calendar v-model="currentDate">
              <template #date-cell="{ data }">
                <div class="calendar-day" @click="handleDayClick(data.day)">
                  <div class="day-number">{{ data.day.split('-')[2] }}</div>
                  <div class="schedule-indicators">
                    <!-- 开始并结束的日程 -->
                    <div v-if="getBothScheduleCount(data.day) > 0" class="schedule-indicator both">
                      {{ getBothScheduleCount(data.day) }}
                    </div>
                    
                    <!-- 单独的日程标记 -->
                    <template v-else>
                      <div v-if="getStartScheduleCount(data.day) > 0" class="schedule-indicator start">
                        {{ getStartScheduleCount(data.day) }}
                      </div>
                      <div v-if="getEndScheduleCount(data.day) > 0" class="schedule-indicator end">
                        {{ getEndScheduleCount(data.day) }}
                      </div>
                    </template>
                    
                    <!-- 无日程提示 -->
                    <div v-if="getTotalScheduleCount(data.day) === 0" class="no-schedule">
                      无日程
                    </div>
                  </div>
                </div>
              </template>
            </el-calendar>
          </div>
          
          <!-- 创建日程表单 -->
          <el-dialog v-model="dialogVisible" title="创建日程" :before-close="cancel">
            <el-form ref="form" :model="form" label-width="100px">
              <el-form-item label="标题">
                <el-input v-model="form.content.title"></el-input>
              </el-form-item>
              
              <el-form-item label="地点">
                <el-input v-model="form.content.location"></el-input>
              </el-form-item>
              
              <el-form-item label="起始时间">
                <div class="time-pickers">
                  <el-date-picker
                    v-model="form.content.begin_time[0]"
                    type="date"
                    placeholder="选择日期"
                    value-format="YYYY-MM-DD"
                  />
                  <el-time-picker
                    v-model="form.content.begin_time[1]"
                    placeholder="选择时间"
                    value-format="HH:mm:ss"
                  />
                </div>
              </el-form-item>
              
              <el-form-item label="结束时间">
                <div class="time-pickers">
                  <el-date-picker
                    v-model="form.content.end_time[0]"
                    type="date"
                    placeholder="选择日期"
                    value-format="YYYY-MM-DD"
                  />
                  <el-time-picker
                    v-model="form.content.end_time[1]"
                    placeholder="选择时间"
                    value-format="HH:mm:ss"
                  />
                </div>
              </el-form-item>
              
              <el-form-item label="内容">
                <el-input type="textarea" v-model="form.content.content" rows="4"></el-input>
              </el-form-item>
              
              <el-form-item label="类型">
                <el-select v-model="form.content.tag" placeholder="请选择类型">
                  <el-option label="工作" value="work"></el-option>
                  <el-option label="学习" value="study"></el-option>
                  <el-option label="生活" value="life"></el-option>
                  <el-option label="娱乐" value="entertainment"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="submit">提交</el-button>
                <el-button @click="cancel">取消</el-button>
              </el-form-item>
            </el-form>
          </el-dialog>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { cloneDeep } from "lodash"
import globalStore from "../utils/GlobalStore.js"
import { AddSchedule } from '../utils/DataManager'

// 初始表单数据
const initialForm = {
  content: {
    tag : "",
    title: "",
    begin_time: ["", ""],
    end_time: ["", ""],
    content: "",
    location: "",
  }
}

export default {
  data() {
    return {
      currentDate: ref(new Date()),
      dialogVisible: ref(false),
      form: cloneDeep(initialForm),
      selectedDate: ""
    }
  },
  computed: {
    // 从全局存储中获取日程数据
    userSchedules() {
      return globalStore.UserSchedules || []
    }
  },
  methods: {
    // 处理日期点击事件
    handleDayClick(date) {
      this.selectedDate = date
      this.form = cloneDeep(initialForm)
      // 设置默认日期为选中的日期
      this.form.content.begin_time[0] = date
      this.form.content.end_time[0] = date
      this.dialogVisible = true
    },
    
    // 获取指定日期的开始日程数量（不包括开始结束同一天的）
    getStartScheduleCount(date) {
      return this.userSchedules.filter(schedule => 
        schedule.content.begin_time?.[0] === date &&
        schedule.content.begin_time?.[0] !== schedule.content.end_time?.[0]
      ).length
    },
    
    // 获取指定日期的结束日程数量（不包括开始结束同一天的）
    getEndScheduleCount(date) {
      return this.userSchedules.filter(schedule => 
        schedule.content.end_time?.[0] === date &&
        schedule.content.begin_time?.[0] !== schedule.content.end_time?.[0]
      ).length
    },
    
    // 获取指定日期的开始并结束日程数量
    getBothScheduleCount(date) {
      return this.userSchedules.filter(schedule => 
        schedule.content.begin_time?.[0] === date &&
        schedule.content.end_time?.[0] === date
      ).length
    },
    
    // 获取指定日期的总日程数量
    getTotalScheduleCount(date) {
      return this.userSchedules.filter(schedule => 
        schedule.content.begin_time?.[0] === date ||
        schedule.content.end_time?.[0] === date
      ).length
    },
    
    // 重置表单
    clean() {
      this.form = cloneDeep(initialForm)
    },
    
    // 提交表单
    submit() {
      // 过滤空值
      const filteredContent = this.filter(this.form.content)
      
      // 验证必填项
      if (!filteredContent.title) {
        ElMessage.warning("标题不能为空")
        return
      }
      
      // 验证时间有效性
      if (filteredContent.begin_time && filteredContent.end_time) {
        const beginDate = new Date(filteredContent.begin_time.join(' '))
        const endDate = new Date(filteredContent.end_time.join(' '))
        
        if (beginDate > endDate) {
          ElMessage.warning("结束时间不能早于开始时间")
          return
        }
      }
      
      // 添加日程
      AddSchedule({
        id: Date.now(),
        content: filteredContent
      })
      
      ElMessage.success("日程创建成功")
      this.dialogVisible = false
      this.clean()
    },
    
    // 过滤空值
    filter(data) {
      const result = {}
      
      Object.keys(data).forEach(key => {
        const value = data[key]
        
        // 处理时间数组
        if (Array.isArray(value) && key.includes('_time')) {
          // 检查日期和时间是否有效
          const dateValid = value[0] && value[0].trim() !== ''
          const timeValid = value[1] && value[1].trim() !== ''
          
          // 只有当日期有效时才保留
          if (dateValid) {
            result[key] = [value[0], timeValid ? value[1] : "00:00:00"]
          }
        } 
        // 处理其他值
        else if (typeof value === 'string' && value.trim() !== '') {
          result[key] = value
        }
        // 处理其他非空值
        else if (value !== null && value !== undefined && value !== '') {
          result[key] = value
        }
      })
      
      return result
    },
    
    // 取消操作
    cancel() {
      ElMessageBox.confirm(
        "确定取消创建日程？",
        "警告",
        {
          confirmButtonText: "确认",
          cancelButtonText: "返回",
        }
      ).then(() => {
        this.dialogVisible = false
        this.clean()
      }).catch(() => {
        // 用户点击了返回，不做操作
      })
    }
  }
}
</script>

<style scoped>
.calendar-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.calendar-day {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 5px;
  cursor: pointer;
}

.calendar-day:hover {
  background-color: #f5f7fa;
}

.day-number {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.schedule-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 24px;
  align-items: center;
}

.schedule-indicator {
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.start {
  background-color: #409eff; /* 蓝色 - 开始日程 */
}

.end {
  background-color: #67c23a; /* 绿色 - 结束日程 */
}

.both {
  background-color: #e6a23c; /* 橙色 - 开始并结束 */
}

.no-schedule {
  color: #909399;
  font-size: 12px;
}

.time-pickers {
  display: flex;
  gap: 10px;
}

.time-pickers > * {
  flex: 1;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-button {
  margin-right: 10px;
}

.el-select, .el-input, .el-textarea {
  width: 100%;
}

/* 颜色图例样式 */
.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.color-box {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.start-color {
  background-color: #409eff;
}

.end-color {
  background-color: #67c23a;
}

.both-color {
  background-color: #e6a23c;
}
</style>
