<template>
  <div class="login-container">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="loginForm" 
      label-width="120px"
      class="login-form"
    >
      <h2 class="title">系统登录</h2>
      
      <!-- 用户名输入框 -->
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="form.username" 
          placeholder="请输入用户名"
          clearable
        />
      </el-form-item>
      
      <!-- 密码输入框 -->
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="form.password" 
          type="password"
          placeholder="请输入密码"
          show-password
          clearable
        />
      </el-form-item>
      
      <!-- 服务器地址输入框 -->
      <!-- <el-form-item label="服务器地址" prop="serverURL">
        <el-input 
          v-model="form.serverURL" 
          placeholder="请输入服务器地址"
          clearable
        />
      </el-form-item> -->
      
      <!-- 按钮区域 -->
      <el-form-item>
        <el-button 
        type="primary" 
        @click="handleLogin"
        :loading="loading"
        class="login-btn"
        >
        登录
        </el-button>
        <el-button 
        @click="handleRegister"
        :loading="loading"
        class="register-btn"
        >
        注册
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios' // 确保已安装axios
// import { ModifyServerURL } from '@/utils/DataManager'
import { useRouter } from 'vue-router'
import globalStore from "../utils/GlobalStore"
import Cookies from 'js-cookie'
import { SyncFromServer } from '@/utils/DataManager'

const router = useRouter();

// 表单数据
const form = reactive({
  username: '',
  password: '',
  serverURL: 'https://whizhou.pythonanywhere.com/'
})

// 表单验证规则
const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
//   serverURL: [
//     { required: true, message: '请输入服务器地址', trigger: 'blur' },
//     { type: 'url', message: '请输入正确的URL地址', trigger: ['blur', 'change'] }
//   ]
})

// 获取表单引用
const loginForm = ref(null)
const loading = ref(false) // 添加加载状态

// 封装请求函数
const PostDataToServer = async (url, data) => {
  try {
    const response = await axios.post(url, data,{
        withCredentials : true
    })
    // const response = await fetch(url, {
    //   method: "POST",
    //   headers: {
    //         "Content-Type": "application/json",
    //       },
    //   body: JSON.stringify(data),
    //   credentials: "include",
    // });
    return response.data
  } catch (error) {
    console.error('请求失败:', error)
    return {
      success: false,
      message: error.response?.data?.message || '请求失败，请检查网络或服务器状态'
    }
  }
}

// 登录处理函数
const handleLogin = async () => {
  // 验证表单
  const valid = await loginForm.value.validate()
  if (!valid) {
    ElMessage.error('请填写正确的表单信息')
    return
  }

  loading.value = true // 开始加载
  try {
    // 发送登录请求
    const result = await PostDataToServer(
      `${form.serverURL}/auth/login`,
      {
        username: form.username,
        password: form.password
      }
    )

    if (result.success) {
      // 登录成功处理
      ElMessage.success('登录成功')
    //   ModifyServerURL(form.serverURL);
      globalStore.UserID = result.user_id;
      Cookies.set("user_id",globalStore.UserID);
      SyncFromServer();
      router.push("/home");
    } else {
      // 登录失败处理
      ElMessage.error(result.message || '登录失败，请检查用户名和密码')
      // 清空密码字段
      form.password = ''
    }
  } catch (error) {
    ElMessage.error('登录请求异常: ' + error.message)
    // 清空密码字段
    form.password = ''
  } finally {
    loading.value = false // 结束加载
  }
}

// 注册处理函数
const handleRegister = async () => {
  // 验证表单（用户名和密码）
  try {
    await loginForm.value.validateField(['username', 'password'])
  } catch (error) {
    ElMessage.error('请填写正确的用户名和密码')
    return
  }

  loading.value = true // 开始加载
  try {
    // 发送注册请求
    const result = await PostDataToServer(
      `${form.serverURL}/auth/register`,
      {
        username: form.username,
        password: form.password
      }
    )

    if (result.success) {
      // 注册成功处理
      ElMessage.success('注册成功，请登录')
      // 清空密码字段
      form.password = ''
    } else {
      // 注册失败处理
      ElMessage.error(result.message || '注册失败，请重试')
      // 清空用户名和密码字段
      form.username = ''
      form.password = ''
    }
  } catch (error) {
    ElMessage.error('注册请求异常: ' + error.message)
    // 清空用户名和密码字段
    form.username = ''
    form.password = ''
  } finally {
    loading.value = false // 结束加载
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-form {
  width: 400px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-btn, .register-btn {
  width: 48%;
}

.login-btn {
  margin-right: 4%;
}
</style>