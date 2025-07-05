<template>
  <div class="homeview">
    <el-container style="height: 100vh;">
      <!-- 左侧导航栏  -->
      <el-aside width="200px">
        <leftbar></leftbar>
      </el-aside>
      
      <!-- 右侧主内容区 -->
      <el-main style="padding: 0; background-color: #EEEEEE;">
        <!-- 顶部控制栏 -->
        <div class="control-bar">
          <!-- 筛选区域 -->
          <div class="filter-area">
            <el-select 
              v-model="statusFilter" 
              placeholder="状态" 
              @change="applyFilters"
              clearable
              size="medium"
              style="width: 150px; margin-right: 10px;"
            >
              <el-option label="全部" value="all" />
              <el-option label="未完成" value="unfinished" />
              <el-option label="已完成" value="finished" />
              <el-option label="已归档" value="archived" />
            </el-select>
            
            <el-select 
              v-model="tagFilter" 
              placeholder="标签" 
              @change="applyFilters"
              clearable
              size="medium"
              style="width: 150px;"
            >
              <el-option label="任意" value="all" />
              <el-option 
                v-for="tag in uniqueTags" 
                :key="tag" 
                :label="tag" 
                :value="tag"
              />
            </el-select>
          </div>
          
          <!-- 创建按钮 -->
          <div class="create-button">
            <create-schedule />
          </div>
        </div>
        
        <!-- 卡片展示区域 -->
        <div class="cards-area">
          <Cards :cards="filteredSchedules" />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import Cards from "../components/Cards.vue"
import CreateSchedule from "../components/CreateSchedule.vue"
import globalStore from "../utils/GlobalStore.js"

export default {
  data() {
    return {
      globalStore,
      statusFilter: 'all',
      tagFilter: 'all',
      filteredSchedules: []
    }
  },
  components: {
    Cards,
    CreateSchedule
  },
  computed: {
    uniqueTags() {
      const tags = new Set();
      this.globalStore.UserSchedules.forEach(schedule => {
        if (schedule.content && schedule.content.tag) {
          tags.add(schedule.content.tag);
        }
      });
      return Array.from(tags);
    }
  },
  methods: {
    applyFilters() {
      this.filteredSchedules = this.globalStore.UserSchedules.filter(schedule => {
        const statusMatch = 
          this.statusFilter === 'all' ||
          (this.statusFilter === 'unfinished' && !schedule.finished && !schedule.archive) ||
          (this.statusFilter === 'finished' && schedule.finished) ||
          (this.statusFilter === 'archived' && schedule.archive);
        
        const tagMatch = 
          this.tagFilter === 'all' ||
          (schedule.content && schedule.content.tag === this.tagFilter);
        
        return statusMatch && tagMatch;
      });
    }
  },
  mounted() {
    this.applyFilters();
  },
  watch: {
    'globalStore.UserSchedules': {
      handler() {
        this.applyFilters();
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.homeview {
  height: 100vh;
  overflow: hidden;
}

/* 顶部控制栏样式 */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 100; /* 确保下拉菜单在上层 */
}

.filter-area {
  display: flex;
  align-items: center;
}

.create-button {
  margin-right: 10px;
}

/* 卡片区域样式 */
.cards-area {
  height: calc(100vh - 60px); /* 减去控制栏高度 */
  padding: 15px;
  overflow-y: auto; /* 允许滚动 */
  box-sizing: border-box;
}

/* 确保下拉菜单在上层 */
.el-select-dropdown {
  z-index: 2000 !important;
}

/* 移除Element Plus默认边距 */
.el-main {
  padding: 0 !important;
}

.el-aside {
  background-color: inherit;
  color: inherit;
  height: 100vh;
}
</style>