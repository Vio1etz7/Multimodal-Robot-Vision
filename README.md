#  宇树机器狗多模态视觉认知终端 (Multi-modal Robot Vision)

本项目是一个基于前后端解耦架构的轻量级机器人视觉认知系统。前端采用 `Vue 3 + Vite + Three.js` 控制台与 3D 空间交互渲染；后端采用 `FastAPI + SegFormer + Open3D` 提供二维图像语义分割与三维点云空间解析的微服务支持。

## 🚀 快速开始 (Quick Start)

### 0. 环境前置要求
* **Node.js** >= 18.x (用于运行前端)
* **Python** >= 3.9 (用于运行后端)
* 建议使用独立的 Python 虚拟环境 (venv 或 conda)

### 1. 准备原始数据
1. 启动后端服务 (Backend)
打开终端，进入后端工程目录并安装依赖：

Bash
cd vision-backend

# 安装 Python 核心依赖 (建议在虚拟环境中执行)
pip install -r requirements.txt -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)

# 启动 FastAPI 微服务
python app.py
服务启动后，API 接口将在 http://127.0.0.1:8000 运行。

3. 启动前端控制台 (Frontend)
打开一个新的终端，进入前端工程目录：

Bash
cd vision-frontend

# 安装前端依赖 (包含 Vue, Element Plus, Three.js 等)
npm install

# 启动 Vite 开发服务器
npm run dev
前端启动后，在浏览器中访问终端输出的本地地址（通常为 http://localhost:5173），即可进入系统控制台。