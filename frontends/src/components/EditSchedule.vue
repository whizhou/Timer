<template>
  <div>
    <el-button
      class="delete-btn" 
      type="text"
      @click="init()"
    >修改</el-button>

    <el-dialog v-model="Visible" title="修改日程" :before-close="cancel" append-to-body>
      <el-form 
        ref="form" 
        :model="form" 
        label-width="100px"
        @submit.native.prevent
      >
        <el-form-item label="标题">
          <el-input v-model="form.content.title"></el-input>
        </el-form-item>
        
        <el-form-item label="地点">
          <el-input v-model="form.content.location"></el-input>
        </el-form-item>
        
        <!-- 起始时间实现 -->
        <el-form-item label="起始时间">
          <div class="time-pickers">
            <el-date-picker
              v-model="tempBeginDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
            />
            <el-time-picker
              v-model="tempBeginTime"
              placeholder="选择时间"
              value-format="HH:mm:ss"
            />
          </div>
        </el-form-item>
        
        <!-- 结束时间实现 -->
        <el-form-item label="结束时间">
          <div class="time-pickers">
            <el-date-picker
              v-model="tempEndDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
            />
            <el-time-picker
              v-model="tempEndTime"
              placeholder="选择时间"
              value-format="HH:mm:ss"
            />
          </div>
        </el-form-item>
        
        <el-form-item label="内容">
          <el-input 
            type="textarea" 
            v-model="form.content.content" 
            :rows="4"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="类型">
          <el-select v-model="form.content.tag" placeholder="请选择类型">
            <el-option label="工作" value="工作"></el-option>
            <el-option label="学习" value="学习"></el-option>
            <el-option label="生活" value="生活"></el-option>
            <el-option label="娱乐" value="娱乐"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="完成情况">
          <el-radio-group v-model="form.finished" @change="setArchive">
            <el-radio :value="true">已完成</el-radio>
            <el-radio :value="false">未完成</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="归档情况">
          <el-radio-group v-model="form.archive" :disabled="form.finished">
            <el-radio :value="true">已归档</el-radio>
            <el-radio :value="false">未归档</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submit" :loading="submitting">确认</el-button>
          <el-button @click="cancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { cloneDeep } from "lodash"
import { AddSchedule, DeleteSchedule, GetSchedule, SyncFromServer } from '../utils/DataManager'
import globalStore from '@/utils/GlobalStore'
import dayjs from 'dayjs'

// 初始表单数据
const initialForm = {
  finished: false,
  archive: false,
  content: {
    tag: "",
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
      form: cloneDeep(initialForm),
      Visible: ref(false),
      OriginId: 0,
      submitting: false,
      
      // 临时时间变量
      tempBeginDate: "",
      tempBeginTime: "",
      tempEndDate: "",
      tempEndTime: "",
    }
  },
  props: {
    origin: {
      required: true,
      type: Object,
    },
  },
  watch: {
    // 监听临时时间变量变化，更新表单
    tempBeginDate() { this.updateTimeArray('begin_time') },
    tempBeginTime() { this.updateTimeArray('begin_time') },
    tempEndDate() { this.updateTimeArray('end_time') },
    tempEndTime() { this.updateTimeArray('end_time') },
  },
  methods: {
    // 处理归档问题

    setArchive () {
      if (this.form.finished==true)
        this.form.archive=true;
    },

    // 更新时间数组
    updateTimeArray(field) {
      this.form.content[field] = [
        this[`temp${field === 'begin_time' ? 'Begin' : 'End'}Date`],
        this[`temp${field === 'begin_time' ? 'Begin' : 'End'}Time`]
      ]
    },
    
    // 复制表单
    init() {
      console.log("Initializing form with origin data:", this.origin)
      
      this.OriginId = cloneDeep(this.origin.id);
      this.form = cloneDeep(initialForm);

      this.form.finished = cloneDeep(this.origin.finished);
      this.form.archive = cloneDeep(this.origin.archive);

      console.log(this.form.finished);
      console.log(this.form.archive);
      
      // 设置临时时间变量
      this.tempBeginDate = this.origin.content.begin_time?.[0] || "";
      this.tempBeginTime = this.origin.content.begin_time?.[1] || "";
      this.tempEndDate = this.origin.content.end_time?.[0] || "";
      this.tempEndTime = this.origin.content.end_time?.[1] || "";
      
      // 更新表单数据
      this.updateTimeArray('begin_time');
      this.updateTimeArray('end_time');
      
      // 复制其他字段
      Object.keys(this.form.content).forEach(key => {
        if (key !== 'begin_time' && key !== 'end_time') {
          if (this.origin.content[key] !== undefined) {
            this.form.content[key] = cloneDeep(this.origin.content[key]);
          }
        }
      });
      
      if (this.origin.type !== undefined) {
        this.form.type = cloneDeep(this.origin.type);
      }
      
      this.Visible = true;
      console.log("Form initialized:", this.form);
    },
    
    // 提交表单
    async submit() {
      console.log("Submit button clicked");
      this.submitting = true;
      
      try {
        console.log("Form data before filtering:", JSON.parse(JSON.stringify(this.form)));
        
        // 过滤空值
        const filteredContent = this.filter(this.form.content)
        
        console.log("Filtered content:", filteredContent);
        
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
        
        console.log("Syncing from server...");
        await SyncFromServer();
        console.log("Sync complete");
        
        console.log("Adding new schedule...");
        const retValue = await AddSchedule({
          finished: this.form.finished,
          archive: this.form.archive,
          content: filteredContent
        });
        console.log("AddSchedule result:", retValue);
        
        console.log("Deleting original schedule ID:", this.OriginId);
        await DeleteSchedule(this.OriginId);
        console.log("Delete complete");
        
        ElMessage.success("日程修改成功")
        this.Visible = false
        this.$emit('change', cloneDeep(retValue));
        
      } catch (error) {
        console.error("Submit error:", error);
        ElMessage.error("操作失败: " + error.message);
      } finally {
        this.submitting = false;
      }
    },
    
    // 过滤空值
    filter(data) {
      const result = {}
      
      Object.keys(data).forEach(key => {
        const value = data[key]
        
        // 处理时间数组
        if (Array.isArray(value) && key.includes('_time')) {
          // 检查日期和时间是否有效
          const dateValid = value[0] && value[0].toString().trim() !== ''
          const timeValid = value[1] && value[1].toString().trim() !== ''
          
          // 只有当日期有效时才保留
          if (dateValid) {
            // 确保日期格式正确
            result[key] = [
              dayjs(value[0]).isValid() ? dayjs(value[0]).format('YYYY-MM-DD') : value[0],
              timeValid ? (dayjs(value[1]).isValid() ? dayjs(value[1]).format('HH:mm:ss') : value[1]) : "00:00:00"
            ]
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
        "确定取消修改日程？",
        "警告",
        {
          confirmButtonText: "确认",
          cancelButtonText: "返回",
        }
      ).then(() => {
        this.Visible = false
      }).catch(() => {
        // 用户点击了返回，不做操作
      })
    }
  }
}
</script>

<style scoped>
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

.delete-btn {
  padding: 0;
  margin: 0;
}
</style>