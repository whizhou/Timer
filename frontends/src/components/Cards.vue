<template>
  <div class="cards-container">
    <el-card 
      v-for="card in cards" 
      :key="card.id" 
      class="auto-size-card"
    >
      <template #header>
        <div class="card-header">
          <span v-if="card.content!=undefined"><b>{{ card.content.title }}<span v-if="card.stauts">(Done)</span></b></span>
          <span v-else><b>无题</b></span>
          <edit-schedule :origin="card"></edit-schedule>
          <el-button 
            class="delete-btn" 
            type="text" 
            @click="deleteCards(card.id)"
          >删除</el-button>
          <el-button 
            class="delete-btn" 
            type="text" 
            @click="done(card)"
          ><span v-if="card.status==true">取消完成</span><span v-else>完成</span></el-button>
        </div>
      </template>
      <div class="card-content">
        <div v-for="(value, key) in card.content">
          <div v-if="key != 'title' && Trans[key]!=undefined && value != ''">
            <p v-if="value.constructor==Array">
              <b>{{ Trans[key] }} : </b>{{ value[0] }} {{ value[1] }}
            </p>
            <p v-else>
              <b>{{ Trans[key] }} : </b>{{ value }}
            </p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import globalStore from '@/utils/GlobalStore';
import Trans from '@/utils/Trans';
import { DeleteSchedule,GetScheduleIndex } from '../utils/DataManager';
import EditSchedule from './EditSchedule.vue';

import { ref, watch } from 'vue';

const props = defineProps({
  cards: {
    type: Array,
    required: true
  }
});

const deleteCards = (id) => {
  DeleteSchedule(id);
};

const done = (card) => {
  let index = GetScheduleIndex(card.id);
  if (globalStore.UserSchedules[index].status!=true) {
    globalStore.UserSchedules[index].status=true;
    card.stauts=true;
  } else {
    globalStore.UserSchedules[index].status=false;
    card.stauts=false;
  }
};

</script>

<style scoped>
.cards-container {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start; /* 重要：避免容器高度拉伸 */
  gap: 16px;
  min-height: 0; /* 防止高度溢出 */
}

.auto-size-card {
  width: auto;
  min-width: 200px;
  max-width: 100%;
  height: auto !important; /* 覆盖可能的高度设置 */
  display: flex;
  flex-direction: column;
}

/* 使用:deep()选择器修改element-plus内部样式 */
.auto-size-card :deep(.el-card__body) {
  flex: none; /* 取消flex填充 */
  height: auto !important; /* 确保高度由内容决定 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.delete-btn {
  padding: 0;
  margin: 0;
}

.card-content {
  height: auto; /* 内容高度自适应 */
  overflow: hidden; /* 防止内容溢出 */
}

.card-content p {
  margin: 8px 0;
  word-break: break-word;
}
</style>