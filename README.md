<div align="center">

  <img src="https://paiad-blog.vercel.app/sunflower.png" width="160" />

  <h1>paiad-admin</h1>

</div>

> [!NOTE]
> 喜欢 `paiad-admin`？请在 GitHub 上为我们点亮一颗 ⭐️！您的支持是我们不断优化的动力！

## 概述

`paiad-admin` 是一个优雅且功能强大的全栈管理系统，包含前端管理界面、后端API服务和AI模型服务。项目基于现代化技术栈构建，提供完整的用户管理、权限控制、数据可视化和AI图像识别功能。

## 项目架构

### 🎨 前端架构 (Vue3 + Element Plus)

**技术栈：**
- Vue3 + Composition API
- Vite5 构建工具
- TypeScript 类型支持
- Element Plus UI组件库
- Pinia 状态管理
- UnoCSS 原子化CSS
- Vue Router 路由管理

**核心功能：**
- 🔐 用户认证与权限管理
- 📊 数据可视化图表 (基于 AntV G2/G6)
- 🌍 多语言国际化支持
- 🎨 多主题切换 (明暗模式)
- 📱 响应式设计，完美适配移动端
- 🔄 自动生成路由系统
- 📄 内置错误页面 (403/404/500)

### 🚀 后端架构 (Spring Boot + Sa-Token)

**技术栈：**
- Spring Boot 3.x
- Sa-Token 权限认证框架
- MyBatis-Plus ORM框架
- Redis 缓存存储
- MQTT 消息通信
- Knife4j API文档
- MySQL 数据库

**核心功能：**
- 🔑 JWT Token 鉴权机制
- 👥 用户注册、登录、权限控制
- 📡 MQTT 轻量级消息通信
- 🗄️ 分布式 Session 管理
- 📚 自动生成API文档
- 🔄 RESTful API 设计

### 🤖 AI服务架构 (FastAPI + YOLO)

**技术栈：**
- FastAPI 高性能API框架
- YOLO11 目标检测模型
- Ultralytics 深度学习框架
- PIL 图像处理
- MySQL 数据存储

**核心功能：**
- 🖼️ 图像上传与处理
- 🎯 实时目标检测
- 📈 检测结果可视化
- 📊 检测历史记录管理
- ⚙️ 模型参数动态调整

## 项目结构

```
paiad-admin/
├── src/                          # 前端源码
│   ├── components/               # 公共组件
│   │   ├── advanced/            # 高级组件
│   │   ├── common/              # 通用组件
│   │   └── custom/              # 自定义组件
│   ├── views/                   # 页面组件
│   │   ├── home/                # 首页
│   │   ├── manage/              # 管理页面
│   │   ├── user-center/         # 用户中心
│   │   └── yolo/                # AI检测页面
│   ├── store/                   # Pinia状态管理
│   ├── router/                  # 路由配置
│   ├── service/                 # API服务
│   ├── utils/                   # 工具函数
│   └── styles/                  # 样式文件
├── paiad-fast/                  # 后端服务
│   ├── paiad-common/            # 公共模块
│   ├── paiad-core/              # 核心模块
│   ├── paiad-framework/         # 框架模块
│   ├── paiad-server/            # 服务模块
│   └── sql/                     # 数据库脚本
├── packages/                    # 工具包
│   ├── utils/                   # 工具函数包
│   ├── hooks/                   # 自定义Hooks
│   ├── materials/               # 物料组件
│   └── scripts/                 # 构建脚本
├── yolo_server.py              # AI检测服务
└── build/                      # 构建配置
```

## 快速开始

### 环境准备

- **Node.js** >= 18.20.0
- **pnpm** >= 8.7.0
- **Java** >= 17
- **MySQL** >= 8.0
- **Redis** >= 6.0
- **Python** >= 3.8

### 前端启动

```bash
# 克隆项目
git clone https://github.com/paiad/paiad-admin.git
cd paiad-admin

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

### 后端启动

```bash
# 进入后端目录
cd paiad-fast

# 配置数据库连接 (application.yml)
# 启动Redis服务

# 运行后端服务
mvn spring-boot:run
```

## 核心模块说明

### 📦 Packages 工具包

- **@sa/utils**: 通用工具函数库
- **@sa/hooks**: Vue3 自定义Hooks
- **@sa/materials**: 物料组件库
- **@sa/scripts**: 项目构建脚本
- **@sa/color**: 颜色处理工具
- **@sa/axios**: HTTP请求封装
- **@sa/alova**: 请求状态管理

### 🎯 核心功能模块

- **用户管理**: 注册、登录、权限控制
- **数据可视化**: 图表展示、数据分析
- **AI检测**: 图像识别、目标检测
- **系统管理**: 菜单管理、角色权限
- **多语言**: 中英文切换支持

## 开发指南

### 环境配置

- `.env` - 基础环境变量
- `.env.development` - 开发环境配置
- `.env.production` - 生产环境配置
- `.env.test` - 测试环境配置

### 构建部署

```bash
# 开发环境
pnpm dev

# 测试环境构建
pnpm build:test

# 生产环境构建
pnpm build
```

## 许可证

`paiad-admin` 采用 [MIT 许可证](./LICENSE) © 2025 Paiad，仅供学习参考。商业使用需保留 [soybean-admin](https://github.com/soybeanjs/soybean-admin) 的原始作者版权信息，并遵守其 MIT 许可证条款。作者不对软件使用中的任何风险承担责任。
