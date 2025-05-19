
<template>
  <div id="container" style="width:90%;height: 90%;">

    <div id="menu" style="height:100%;width:15%;float:left;">
      <leftbar></leftbar>  
    </div>
    
    <div id="content" style="height:100%;width:85%;float:right;">
    
      <el-calendar>
        
        <template
            slot="dateCell"
            slot-scope="{date, data}">
            <p :class="data.isSelected ? 'is-selected' : ''">
            {{ data.day.split('-').slice(1).join('-') }} {{ data.isSelected ? '✔️' : ''}}
            </p>
        </template>

    </el-calendar>

    </div>

  </div>
  
</template>

<style>
  .is-selected {
    color: #1989FA;
  }
</style>