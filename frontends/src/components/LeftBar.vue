
<template>

<div  style="height: 100%;width: 100%;">
    <el-row class="tac" style="height: 100%;width: 100%;">
        <el-col :span="3" style="height: 100%;width: 100%;">
            <h2>Timer_demo</h2>
            <el-menu default-active="/" class="MainMenu" router="true" style="height: 100%;width: 100%;">
                <el-menu-item index="/">
                        <i class="el-icon-menu"></i>
                        <span slot="title">主页</span>
                </el-menu-item>
                <el-menu-item index="/dpchat">
                    <i class="el-icon-document"></i>
                    <span slot="title">AI助手</span>
                </el-menu-item>
                <el-menu-item index="/calendar">
                    <i class="el-icon-document"></i>
                    <span slot="title">日历（待完成）</span>
                </el-menu-item>
            </el-menu>
        </el-col>
    </el-row>
</div>

</template>

<style>
html,
body,
#app,
.el-container {
  height: 100%;
  width: 100%;
}
.el-menu {
	border-right:0!important;
}
</style>