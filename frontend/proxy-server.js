const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const config = require('./config');
const app = express();

// 启用CORS
app.use(cors({
  origin: `http://localhost:${config.DEV_PORT}`,
  credentials: true
}));

// 处理静态文件请求，包括 favicon.ico
app.get('/favicon.ico', (req, res) => {
  res.sendFile(require('path').join(__dirname, 'public', 'favicon.ico'));
});

// 处理其他静态文件请求
app.get(/^\/static\/(.+)/, (req, res) => {
  const filePath = req.path.replace('/static/', '');
  res.sendFile(require('path').join(__dirname, 'public', filePath));
});

// 代理所有/api请求到后端服务器
app.use('/api', createProxyMiddleware({
  target: config.API_SERVER,
  changeOrigin: true,
  secure: false,
  onProxyReq: (proxyReq, req) => {
    // 保持原始请求头
    if (req.headers.authorization) {
      proxyReq.setHeader('Authorization', req.headers.authorization);
    }
  }
}));

app.listen(config.PROXY_PORT, () => {
  console.log(`代理服务器运行在 http://localhost:${config.PROXY_PORT}`);
  console.log(`代理 /api/* 到 ${config.API_SERVER}`);
});
