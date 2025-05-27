
<template>
  <div id="container" style="width:90%;height: 90%;">

    <div id="menu" style="height:100%;width:15%;float:left;">
      <leftbar></leftbar>  
    </div>
    
    <div id="content" style="background-color:#EEEEEE;height:100%;width:85%;overflow: auto;">
    
      <div id="output" style="width: 60%;float: left;">
        <Cards @delcards="delcards" v-for="item in cardList" :key="item.id" :cardData="item" />
      </div>

      <div id="input" style="width: 40%;float: right;">
        <Form @addcards="addcards"></Form>
        <button @click = "__test_get">测试：拉取信息</button>
        <button @click = "__test_post">测试：上传信息</button>
      </div>

    </div>
  
  </div>
</template>

<script>
import Cards from '../components/Cards.vue';
import Form from '../components/Form.vue';
import axios from 'axios';
import * as datamanager from '../components/DataManager.js'

export default {
  name: 'App',
  components: {
    Cards,
    Form
  },
  data() {
    return {
      cardList: [
        // { id: 1, title: '卡片标题1', dateTime: '2021-09-01', image: 'image-url-1.jpg' },
        // { id: 2, title: '卡片标题2', dateTime: '2021-09-02', image: 'image-url-2.jpg' },
        // // 更多卡片数据...
      ]
    };
  },
  methods : {
    delcards(id) {
      for (var i=id;i<this.cardList.length;i++)
        this.cardList[i].id=i;
      this.cardList.splice(id-1,1);
    },
    addcards(data) {
      data.id=this.cardList.length;
      this.cardList.push(data);
    },
    __test_get () {
      datamanager.GetDataFromServer();
      this.cardList=datamanager.Schedules();
      
    },
    __test_post () {
      datamanager.ModifySchedules(this.cardList);
      datamanager.PostDataToServer();
    },
  }
}
</script>


<style>

  .right-bottom-fixed {

    position: fixed;


    bottom: 0;


    right: 0;


  }

</style>