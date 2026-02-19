import { createApp } from 'vue';
import App from './App.vue';
import axiosInstance from '@/utils/axios';
import router from './router';

// 启动时自动设置token
const token = localStorage.getItem('token');
if (token) {
  axiosInstance.defaults.headers.common['Authorization'] = token;
}

const app = createApp(App);
app.use(router);
app.mount('#app');
