前端使用说明
===========

功能
- 开始/停止屏幕共享
- 截取当前屏幕画面并预览/下载
- 将最后一张截图上传到后端（FastAPI）

技术栈
- React 18 + Vite
- 现代浏览器原生 API (MediaDevices, Canvas)

开发
```bash
npm install
npm run dev
```

构建
```bash
npm run build
```

上传配置
- 页面里可以修改后端地址（默认 `http://localhost:8000`）
- 后端启动方式见 `@backend/README.md`

注意
- 屏幕共享通常在 `https` 或 `localhost` 环境下可用

