<template>
  <el-form ref="form" :model="form" label-width="80px">
    <el-form-item label="标题">
        <el-input v-model="form.name"></el-input>
    </el-form-item>
    <el-form-item label="地点">
        <el-input v-model="form.region"></el-input>
    </el-form-item>
    <el-form-item label="时间">
        <el-col :span="11">
        <el-date-picker type="date" placeholder="选择日期" v-model="form.date1" style="width: 100%;"></el-date-picker>
        </el-col>
        <el-col class="line" :span="2">-</el-col>
        <el-col :span="11">
        <el-time-picker placeholder="选择时间" v-model="form.date2" style="width: 100%;"></el-time-picker>
        </el-col>
    </el-form-item>
    <el-form-item label="内容">
        <el-input type="textarea" v-model="form.cont"></el-input>
    </el-form-item>
    <el-form-item label="补充">
        <el-input type="textarea" v-model="form.extra"></el-input>
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
          name: '',
          region: '',
          date1: '',
          date2: '',
          cont:'',
          extra:'',
        }
      }
    },
    methods: {
      clean () {
        this.form.id=0;
        this.form.name=this.form.region=this.form.date1=this.form.date2=this.form.cont=this.form.extra="";
      },
      onSubmit() {
        let ndata=cloneDeep(this.form)
        this.clean()
        this.$emit("addcards",ndata);
      }
    }
  }
</script>