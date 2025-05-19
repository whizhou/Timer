<template>
  <el-card class="box-card">
  <div slot="header" class="clearfix">
    <span><h3>{{cardData.name}}</h3></span>
    <el-button style="float: right; padding: 3px 0" type="text" @click="del(cardData.id)">删除</el-button>
  </div>
  <div class="text item">
    <b>地点：</b>{{ cardData.region }}
  </div>
  <div class="text item">
    <b>时间：</b>{{ cardData.date2 }}
  </div>
  <div class="text item">
    <b>内容：</b>{{ cardData.cont }}
  </div>
  <div class="text item">
    <b>补充：</b>{{ cardData.extra }}
  </div>
</el-card>

</template>

<script>
export default {
  name: 'Card',
  props: {
    cardData: {
      type: Object,
      required: true
    }
  },
  methods : {
    del (id) {
      this.$emit("delcards",id)
    }
  }
}
</script>

<style>
  .text {
    font-size: 14px;
  }

  .item {
    margin-bottom: 18px;
  }

  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }

  .box-card {
    width: 480px;
  }
</style>
<style>
@media (max-width: 768px) {
  .container {
    flex-direction: column;
    align-items: center;
  }

  .el-card {
    width: 90%;
    margin-bottom: 20px;
  }
}

@media (min-width: 769px) {
  .el-card {
    width:60%;
  }
}
</style>