<template>
  <div class="calendar">
    <el-container>
      <el-aside width="200px"> <leftbar></leftbar> </el-aside>
      <el-container style="background-color:#EEEEEE">
        <!-- 日程统计界面 -->
        <el-main class="statistics-container">
          <!-- 标题 -->
          <div class="header">
            <h1>日程统计概览</h1>
            <p>查看您的任务完成情况和分布</p>
          </div>
          
          <!-- 统计卡片 -->
          <el-row :gutter="20" class="stats-cards">
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="card-content">
                  <div class="icon total">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="info">
                    <h3>总任务数</h3>
                    <p>{{ totalSchedules }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="card-content">
                  <div class="icon completed">
                    <el-icon><CircleCheck /></el-icon>
                  </div>
                  <div class="info">
                    <h3>已完成</h3>
                    <p>{{ completedSchedules }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="card-content">
                  <div class="icon pending">
                    <el-icon><Clock /></el-icon>
                  </div>
                  <div class="info">
                    <h3>未完成</h3>
                    <p>{{ uncompletedSchedules }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="card-content">
                  <div class="icon rate">
                    <el-icon><DataAnalysis /></el-icon>
                  </div>
                  <div class="info">
                    <h3>完成率</h3>
                    <p>{{ completionRate }}%</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- 图表区域 -->
          <el-row :gutter="20" class="chart-area">
            <el-col :span="12">
              <el-card class="chart-card">
                <h3>任务完成情况分布</h3>
                <div ref="pieChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="chart-card">
                <h3>每日任务分布</h3>
                <div ref="barChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- 趋势图 -->
          <el-row class="trend-chart">
            <el-col :span="24">
              <el-card class="chart-card">
                <h3>任务完成趋势</h3>
                <div ref="lineChart" style="height: 350px;"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import {
  Document,
  CircleCheck,
  Clock,
  DataAnalysis
} from '@element-plus/icons-vue';
import globalStore from "../utils/GlobalStore.js";

export default {
  components: {
    Document,
    CircleCheck,
    Clock,
    DataAnalysis
  },
  setup() {
    // 计算属性
    const totalSchedules = computed(() => globalStore.UserSchedules.length);
    const completedSchedules = computed(() => 
      globalStore.UserSchedules.filter(s => s.finished).length
    );
    const uncompletedSchedules = computed(() => 
      globalStore.UserSchedules.filter(s => !s.finished).length
    );
    const completionRate = computed(() => {
      if (totalSchedules.value === 0) return 0;
      return Math.round((completedSchedules.value / totalSchedules.value) * 100);
    });
    
    // 按日期分组统计
    const schedulesByDate = computed(() => {
      const groups = {};
      globalStore.UserSchedules.forEach(schedule => {
        // 检查end_time是否存在且格式正确
        if (schedule.content && schedule.content.end_time && Array.isArray(schedule.content.end_time)) {
          const date = schedule.content.end_time[0];
          if (!groups[date]) {
            groups[date] = {
              total: 0,
              completed: 0,
              uncompleted: 0
            };
          }
          groups[date].total++;
          if (schedule.finished) {
            groups[date].completed++;
          } else {
            groups[date].uncompleted++;
          }
        }
      });
      return groups;
    });
    
    // 图表引用
    const pieChart = ref(null);
    const barChart = ref(null);
    const lineChart = ref(null);
    
    // 初始化图表
    onMounted(() => {
      renderPieChart();
      renderBarChart();
      renderLineChart();
    });
    
    // 监听数据变化
    watch(() => globalStore.UserSchedules, () => {
      renderPieChart();
      renderBarChart();
      renderLineChart();
    }, { deep: true });
    
    // 渲染饼图
    const renderPieChart = () => {
      if (!pieChart.value) return;
      
      const chart = echarts.init(pieChart.value);
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          data: ['已完成', '未完成']
        },
        series: [
          {
            name: '任务状态',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: completedSchedules.value, name: '已完成', itemStyle: { color: '#36a16b' } },
              { value: uncompletedSchedules.value, name: '未完成', itemStyle: { color: '#e6a23c' } }
            ]
          }
        ]
      };
      chart.setOption(option);
      
      // 响应式调整
      window.addEventListener('resize', () => chart.resize());
    };
    
    // 渲染柱状图
    const renderBarChart = () => {
      if (!barChart.value) return;
      
      const dates = Object.keys(schedulesByDate.value).sort();
      const completedData = [];
      const uncompletedData = [];
      
      dates.forEach(date => {
        completedData.push(schedulesByDate.value[date].completed);
        uncompletedData.push(schedulesByDate.value[date].uncompleted);
      });
      
      const chart = echarts.init(barChart.value);
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['已完成', '未完成']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value',
          name: '任务数量'
        },
        series: [
          {
            name: '已完成',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: completedData,
            itemStyle: { color: '#36a16b' }
          },
          {
            name: '未完成',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: uncompletedData,
            itemStyle: { color: '#e6a23c' }
          }
        ]
      };
      chart.setOption(option);
      
      // 响应式调整
      window.addEventListener('resize', () => chart.resize());
    };
    
    // 渲染趋势图
    const renderLineChart = () => {
      if (!lineChart.value) return;
      
      const dates = Object.keys(schedulesByDate.value).sort();
      const totalData = [];
      const completedData = [];
      const completionRates = [];
      
      dates.forEach(date => {
        const group = schedulesByDate.value[date];
        totalData.push(group.total);
        completedData.push(group.completed);
        const rate = group.total > 0 ? Math.round((group.completed / group.total) * 100) : 0;
        completionRates.push(rate);
      });
      
      const chart = echarts.init(lineChart.value);
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: ['任务总数', '已完成任务', '完成率']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates
        },
        yAxis: [
          {
            type: 'value',
            name: '任务数量',
            min: 0
          },
          {
            type: 'value',
            name: '完成率',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}%'
            }
          }
        ],
        series: [
          {
            name: '任务总数',
            type: 'line',
            stack: 'Total',
            areaStyle: {},
            emphasis: {
              focus: 'series'
            },
            data: totalData,
            itemStyle: { color: '#409eff' }
          },
          {
            name: '已完成任务',
            type: 'line',
            stack: 'Total',
            areaStyle: {},
            emphasis: {
              focus: 'series'
            },
            data: completedData,
            itemStyle: { color: '#36a16b' }
          },
          {
            name: '完成率',
            type: 'line',
            yAxisIndex: 1,
            symbol: 'circle',
            symbolSize: 8,
            data: completionRates,
            itemStyle: { color: '#e6a23c' }
          }
        ]
      };
      chart.setOption(option);
      
      // 响应式调整
      window.addEventListener('resize', () => chart.resize());
    };
    
    return {
      totalSchedules,
      completedSchedules,
      uncompletedSchedules,
      completionRate,
      pieChart,
      barChart,
      lineChart
    };
  }
};
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  background-color: #f5f7fa;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.header p {
  color: #909399;
  font-size: 16px;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  color: white;
}

.icon.total {
  background-color: #409eff;
}

.icon.completed {
  background-color: #36a16b;
}

.icon.pending {
  background-color: #e6a23c;
}

.icon.rate {
  background-color: #f56c6c;
}

.info h3 {
  margin: 0;
  font-size: 16px;
  color: #909399;
  margin-bottom: 8px;
}

.info p {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.chart-area {
  margin-bottom: 30px;
}

.trend-chart {
  margin-bottom: 30px;
}

.chart-card {
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.chart-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}
</style>
