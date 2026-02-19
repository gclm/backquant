/**
 * 项目统一配置文件
 */

const DEV_PORT = 8080;
const PROXY_PORT = 3000;
const API_SERVER = process.env.VUE_APP_API_SERVER || 'http://127.0.0.1:54321';

module.exports = {
  DEV_PORT,
  PROXY_PORT,
  // 后端 API 服务器地址
  API_SERVER
};
