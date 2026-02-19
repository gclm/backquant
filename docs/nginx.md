# Nginx 反向代理说明

生产环境建议通过 Nginx 将前端、后端 API 和 Jupyter 统一到同一域名下。

## 关键点

- SPA 前端：`root` 指向前端构建目录，`try_files` 回退到 `index.html`。
- API 反代：`/api/` 代理到后端服务（例如 `127.0.0.1:54321`）。
- Jupyter 反代：`/jupyter/` 代理到 Jupyter（例如 `127.0.0.1:8888`），并开启 WebSocket 支持。
- 生产环境可启用 HTTPS 与安全头。

## 示例配置（简化版）

```nginx
server {
    listen 80;
    server_name example.com;

    root /usr/share/nginx/html/backtest;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:54321/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /jupyter/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
}
```

## 参考

你当前机器上的 `/etc/nginx/conf.d/backtest.conf` 里包含了：

- HTTP -> HTTPS 重定向
- SSL 证书配置
- IP allow/deny 白名单控制
- 静态资源缓存策略

可以直接按需裁剪和替换域名、证书路径、反代目标端口。
