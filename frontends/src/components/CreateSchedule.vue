<template>
  <div>

    <!-- AAA -->
    <el-button plain @click="Visible = true">
      <b>创建日程</b>
    </el-button>
    <!-- AAA -->

    <el-dialog v-model="Visible" title="创建日程" :before-close="cancel">
      <el-form ref="form" :model="form" label-width="100px">
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
        
        <!-- 结束时间实现 -->
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
          <el-input type="textarea" v-model="form.content.content" :rows="4"></el-input>
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
  </div>
</template>

<script lang="ts">
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { cloneDeep } from "lodash"
import { AddSchedule } from '../utils/DataManager'

// 初始表单数据
const initialForm = {
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
      Visible: ref(false)
    }
  },
  methods: {
    // 重置表单到初始状态
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
        type: this.form.type,
        content: filteredContent
      })
      
      ElMessage.success("日程创建成功")
      this.Visible = false
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
        this.Visible = false
        this.clean()
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
</style>