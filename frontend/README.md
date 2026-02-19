# frontend

## 开发

```bash
npm install
npm run serve
```

## 配置

- 构建时环境变量示例见 `.env.example`。
- `VUE_APP_API_SERVER` 用于本地开发代理目标（`vue.config.js`）。
- `VUE_APP_API_BASE` 用于构建时 API 基址（可为空，表示同域）。
- `public/config.js` 支持运行时覆盖 API 基址，不需要重新构建。

## 构建

```bash
npm run build
```
