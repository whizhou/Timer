<template>
  <el-form ref="form" :model="form" label-width="80px">
    <el-form-item label="标题">
        <el-input v-model="form.title"></el-input>
    </el-form-item>
    <el-form-item label="地点">
        <el-input v-model="form.content.location"></el-input>
    </el-form-item>
    <el-form-item label="时间">
        <el-col :span="11">
        <el-date-picker type="date" placeholder="选择日期" v-model="form.content.begin_time" style="width: 100%;"></el-date-picker>
        </el-col>
        <el-col class="line" :span="2">-</el-col>
        <el-col :span="11">
        <el-time-picker placeholder="选择时间" v-model="form.content.end_time" style="width: 100%;"></el-time-picker>
        </el-col>
    </el-form-item>
    <el-form-item label="内容">
        <el-input type="textarea" v-model="form.content.content"></el-input>
    </el-form-item>
    <el-form-item label="类型">
        <el-input type="textarea" v-model="form.type"></el-input>
    </el-form-item>
    <el-form-item>
        <el-button type="primary" @click="onSubmit">提交</el-button>
        <el-button @click="clean">取消</el-button>
    </el-form-item>
  </el-form>
</template>
<script>
  import { cloneDeep } from "lodash";
  export default {
    data() {
      return {
        form: {
          id: 0,
          title : "",
          type : "",
          content : {
            begin_time : "",
            end_time : "",
            content : "",
            location : "",
          }
        }
      }
    },
    methods: {
      clean () {
        this.form.id=0;
        this.form.title=
        this.form.type=
        this.form.content.content=
        this.form.content.begin_time=
        this.form.content.end_time=
        this.form.content.location="";
      },
      onSubmit() {
        let ndata=cloneDeep(this.form)
        this.clean()
        this.$emit("addcards",ndata);
      }
    }
  }
</script>