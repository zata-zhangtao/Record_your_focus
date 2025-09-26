# 自动活动记录器 (Automatic Activity Recorder)

一个自动截图并使用AI分析用户活动的Python应用程序，每3分钟记录一次用户当前在做什么。

## 功能特性

- 🔄 **自动截图**: 每3分钟自动捕获屏幕截图
- 🤖 **AI分析**: 使用阿里云千问VL模型分析用户活动
- 📊 **活动记录**: 持久化存储活动记录和分析结果
- 🔧 **LangGraph工作流**: 使用LangGraph框架进行任务编排
- 📈 **统计分析**: 提供详细的使用统计信息
- 📤 **数据导出**: 支持导出活动记录到JSON文件

## 系统要求

- Python 3.8+
- 阿里云DashScope API Key
- 支持截图的操作系统 (Linux/Windows/macOS)

## 安装

1. 克隆或下载项目
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量 (可选):
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置你的API Key
   ```

## 配置

### API Key配置

你需要一个阿里云DashScope的API Key:

1. 访问 [DashScope控制台](https://dashscope.console.aliyun.com/)
2. 创建API Key
3. 在 `config.py` 中设置API Key，或通过环境变量 `DASHSCOPE_API_KEY`

### 模型配置

- 默认使用 `qwen-vl-plus` 模型
- 可在 `config.py` 中修改模型名称
- 支持的模型: `qwen-vl-plus`, `qwen-vl-max` 等

## 使用方法

### 🖥️ 图形界面版本 (推荐)
```bash
python main_gui.py
# 或使用 uv
uv run main_gui.py
```
启动图形界面，提供以下功能：
- **可视化控制**: 直观的启动/停止录制按钮
- **实时状态**: 显示录制状态和最近活动
- **设置管理**: 可视化配置API、模型、提示词等
- **时间查询**: 选择时间段或分钟数，AI智能分析活动模式
- **活动浏览**: 筛选、搜索、预览截图
- **系统托盘**: 后台运行支持

### 📟 命令行版本

#### 连续录制模式 (默认)
```bash
python main.py
# 或
uv run main.py
```
每3分钟自动截图并分析活动，按 Ctrl+C 停止。

#### 单次录制
```bash
python main.py --single
```
执行一次截图和分析，然后退出。

#### 查看统计信息
```bash
python main.py --stats
```
显示活动记录的统计信息，包括成功率、最近活动等。

#### 导出数据
```bash
python main.py --export [输出文件名]
```
导出活动记录到JSON文件，如果不指定文件名会自动生成。

#### 设置日志级别
```bash
python main.py --log-level DEBUG
```

## 文件结构

```
auto_record_my_activates/
├── main.py                    # 命令行版本入口
├── main_gui.py               # GUI版本入口 ⭐️
├── config.py                 # 配置管理
├── screenshot_agent.py       # 截图功能
├── analysis_agent.py         # AI分析功能
├── storage.py                # 数据存储
├── workflow.py               # LangGraph工作流
├── gui/                      # GUI界面模块 ⭐️
│   ├── __init__.py
│   ├── main_window.py        # 主窗口
│   ├── settings_dialog.py    # 设置对话框
│   ├── time_query_widget.py  # 时间查询组件
│   ├── config_manager.py     # GUI配置管理
│   └── widgets/              # GUI组件
│       ├── __init__.py
│       ├── status_widget.py  # 状态显示组件
│       ├── activity_list.py  # 活动列表组件
│       └── screenshot_preview.py # 截图预览组件
├── requirements.txt          # 依赖列表
├── .env.example             # 环境变量示例
├── README.md                # 说明文档
├── screenshots/             # 截图存储目录
├── activity_log.json        # 活动记录文件
├── gui_config.json          # GUI配置文件
└── activity_recorder.log    # 日志文件
```

## 输出数据格式

活动记录保存在 `activity_log.json` 文件中，格式如下:

```json
{
  "created_at": "2025-01-20T10:00:00",
  "activities": [
    {
      "timestamp": "2025-01-20T10:03:00",
      "screenshot_path": "screenshots/screenshot_20250120_100300.png",
      "activity_description": "用户正在使用VS Code编写Python代码",
      "analysis_result": {
        "activity_description": "用户正在使用VS Code编写Python代码",
        "confidence": "high",
        "analysis_successful": true,
        "error": null
      },
      "confidence": "high",
      "analysis_successful": true,
      "error": null
    }
  ]
}
```

## 技术架构

- **截图**: 使用 `mss` 库进行快速跨平台截图
- **AI分析**: 直接集成 `DashScope` 原生API，使用 Qwen3-VL-Plus 模型
- **工作流**: 使用 `LangGraph` 进行任务编排和状态管理
- **存储**: JSON文件存储，支持数据导出和清理
- **异步**: 使用 `asyncio` 实现异步任务调度

## 重要更新 (2025-09-25)

### 🎉 新增图形界面版本
- ✅ **PyQt6图形界面** - 用户友好的可视化操作界面
- ✅ **可视化设置管理** - API配置、模型选择、提示词自定义
- ✅ **智能时间查询** - 选择时间段或分钟数，AI分析活动模式
- ✅ **活动数据浏览** - 筛选、搜索、截图预览功能
- ✅ **系统托盘支持** - 后台运行和状态监控

### API集成优化
- ✅ **替换ChatTongyi为DashScope原生API** - 提高稳定性和性能
- ✅ **支持流式响应处理** - 基于官方示例优化响应处理
- ✅ **启用思考模式** - 使用 `enable_thinking=True` 提高分析质量
- ✅ **正确的模型名称** - 更新为 `qwen3-vl-plus` 最新模型

### 技术变更
- 新增 PyQt6 图形界面框架
- 模块化GUI组件设计，易于扩展
- 移除 `langchain-community` 依赖，直接使用 `dashscope` 库
- 优化消息格式，使用DashScope原生格式
- 改进错误处理和响应解析
- 支持base64图片格式的直接分析

## GUI功能特色

### 🎛️ 主控制面板
- **一键启停**: 直观的录制控制按钮
- **实时状态**: 显示录制状态、下次截图倒计时
- **最近活动**: 实时显示最新的AI分析结果
- **截图预览**: 查看最近捕获的截图

### ⚙️ 高级设置
- **录制配置**: 可调节截图间隔(10秒-30分钟)、自动启动
- **API管理**: 可视化配置DashScope API Key和模型选择
- **提示词编辑**: 自定义AI分析提示词，支持模板管理
- **界面主题**: 支持明暗主题切换、紧凑视图
- **数据管理**: 自动清理设置、数据导出和备份

### 📊 智能时间查询 ⭐️
这是用户特别要求的核心功能：

#### 两种查询模式
1. **时间段模式**: 选择开始和结束时间
2. **回溯模式**: 选择过去N分钟的活动

#### AI智能分析
- **活动汇总**: AI自动分析时间段内的主要活动
- **模式识别**: 识别工作模式、效率分析、专注度评估
- **中文输出**: 详细的中文分析报告

#### 快速操作
- **一键查询**: "过去1小时"、"过去3小时"、"今天"等快速选项
- **详细列表**: 显示时间段内所有活动记录
- **导出功能**: 将分析结果导出为文本文件

### 🔍 活动数据浏览
- **高级筛选**: 按日期、成功状态、关键词筛选
- **截图预览**: 点击查看对应的屏幕截图
- **统计信息**: 成功率、活动分布等统计数据
- **批量操作**: 导出选定数据、批量清理

## 性能优化

- 自动清理旧截图 (保留最近50张)
- 自动清理旧活动记录 (保留30天)
- 使用高效的截图库 `mss`
- 异步处理避免阻塞

## 故障排除

### 常见问题

1. **API Key错误**: 检查DashScope API Key是否正确设置
2. **截图失败**: 确保系统支持截图功能，Linux可能需要安装额外依赖
   - 在无显示环境中: `$DISPLAY not set` 错误是正常的
3. **模型调用失败**: 检查网络连接和API配额

### 已解决的问题

#### InvalidParameter错误 (2025-09-25修复)
**错误信息**: `The incremental_output parameter of this model cannot be set to False`

**解决方案**:
- 使用流式响应 (`stream=True`)
- 基于官方示例优化响应处理逻辑
- 正确处理思考过程和答案内容

#### 消息格式错误 (2025-09-25修复)
**错误信息**: `Input should be 'text', 'image', 'audio', 'video' or 'image_hw'`

**解决方案**:
- 替换ChatTongyi为DashScope原生API
- 使用正确的消息格式: `{"image": "data_url", "text": "prompt"}`
- 更新模型名称为 `qwen3-vl-plus`

### 日志查看

检查 `activity_recorder.log` 文件获取详细的错误信息。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！