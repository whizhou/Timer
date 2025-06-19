# 桌宠项目

## 项目概述

这是一个基于PyQt5的桌面宠物应用程序，具有智能交互、动画播放、心情管理等功能。

## 新增功能

### 🎬 退出动画
- 当用户点击右键菜单中的"退出"时，桌宠会根据当前的ID和心情状态播放对应的退出动画
- 退出动画文件路径：`static/charactor/{pet_id}/finish_work/{mood}/`
- 支持的心情类型：Happy、Normal、PoorCondition

### 🔧 代码重构亮点
- **模块化设计**：将功能拆分为独立的模块，提高代码可维护性
- **配置管理**：统一的配置文件管理所有常量和路径
- **类型注解**：添加完整的类型注解，提高代码可读性
- **错误处理**：增强的异常处理和日志输出

## 项目结构

```
pet/
├── config.py                  # 配置管理模块
├── main.py                    # 应用程序入口
├── desktop_pet.py             # 桌宠数据模型
├── desktop_pet_ui.py          # 桌宠UI界面
├── desktop_pet_controller.py  # 桌宠控制器
├── mouse_event_handler.py     # 鼠标事件处理
├── mood.py                    # 心情管理
├── pet_action.py              # 动作管理
├── schedule_manager.py        # 日程管理
├── pet_chat.py                # 聊天功能
├── Bubble.py                  # 气泡消息
└── static/                    # 静态资源
    └── charactor/             # 角色动画
        └── {pet_id}/          # 桌宠ID
            ├── stand/         # 待机动画
            ├── drag/          # 拖拽动画
            ├── chat/          # 聊天动画
            ├── switch_up/     # 心情变好动画
            ├── switch_down/   # 心情变差动画
            └── finish_work/   # 退出动画 ⭐ 新增
                ├── Happy/     # 开心状态退出动画
                ├── Normal/    # 正常状态退出动画
                └── PoorCondition/ # 忙碌状态退出动画
```

## 核心模块说明

### 1. config.py - 配置管理
```python
class PetConfig:
    # 动画类型
    class AnimationType:
        STAND = "stand"
        DRAG = "drag"
        CHAT = "chat"
        FINISH_WORK = "finish_work"  # 新增退出动画
    
    # 心情类型
    class MoodType:
        HAPPY = "Happy"
        NORMAL = "Normal"
        POOR_CONDITION = "PoorCondition"
```

### 2. desktop_pet.py - 数据模型
- 管理桌宠的核心数据和状态
- 支持状态切换和统计信息
- 提供动画路径自动计算

### 3. desktop_pet_controller.py - 控制器
- 核心业务逻辑控制
- 动画状态管理
- 退出流程控制 ⭐ 新增

### 4. desktop_pet_ui.py - UI界面
- 界面渲染和交互
- 退出动画播放 ⭐ 新增
- 气泡消息显示

## 使用方法

### 启动应用
```bash
python main.py
```

### 交互方式
1. **单击** - 显示随机消息
2. **双击** - 启用拖拽模式
3. **拖拽** - 移动桌宠位置
4. **右键菜单**：
   - 聊天 - 打开聊天窗口
   - 退出 - 播放退出动画后关闭 ⭐ 新增功能


## 配置选项

在 `config.py` 中可以调整以下参数：

- `ANIMATION_FRAME_INTERVAL` - 动画帧间隔（毫秒）
- `EXIT_ANIMATION_DURATION` - 退出动画播放时长（毫秒）
- `HOVER_DELAY` - 悬停延迟时间（毫秒）
- `BUBBLE_MAX_WIDTH` - 气泡最大宽度（像素）

## 心情系统

桌宠的心情会根据当前的任务数量自动调整：
- **Happy** - 无任务或任务很少
- **Normal** - 任务数量适中
- **PoorCondition** - 任务繁重

心情变化时会播放相应的过渡动画。


## 待机动作功能

桌宠现在支持自动待机动作功能，会在指定间隔时间内自动执行各种可爱的动作。

### 功能特点

- **自动触发**：每隔30秒（可配置）自动执行待机动作
- **多种动作**：支持完成工作、思考、饥饿、学习、散步等多种待机动作
- **智能避让**：在拖拽或聊天时不会触发待机动作
- **个性化消息**：每种待机动作都有对应的可爱消息
- **动画支持**：使用现有的动画资源，如finish_work文件夹等

### 配置方法

可以通过修改`config.py`中的参数来自定义待机动作：

```python
# 修改待机动作间隔时间（秒）
PetConfig.set_idle_action_interval(45)  # 设置为45秒

# 修改待机动作持续时间（毫秒）
PetConfig.set_idle_action_duration(4000)  # 设置为4秒
```

### 支持的待机动作

当前支持以下待机动作类型：
- `finish_work` - 完成工作动作
- `think` - 思考动作  
- `hunger` - 饥饿动作
- `study` - 学习动作
- `walk` - 散步动作

### 添加新的待机动作

1. 在`static/charactor/{pet_id}/`目录下添加新的动作文件夹
2. 在`config.py`的`IdleActionType`类中添加新的动作类型
3. 在控制器的`_get_idle_action_message`方法中添加对应的消息

### 配置参数说明

- `IDLE_ACTION_INTERVAL`: 待机动作触发间隔（默认30秒）
- `IDLE_ACTION_DURATION`: 待机动作持续时间（默认3000毫秒）  
- `IDLE_ACTION_MIN_INTERVAL`: 最小待机动作间隔（15秒）
- `IDLE_ACTION_MAX_INTERVAL`: 最大待机动作间隔（60秒）

### 注意事项

- 待机动作只会在桌宠空闲时触发（非拖拽、非聊天状态）
- 系统会自动检测动画文件夹是否存在，只使用可用的动作
- 待机动作结束后会自动恢复到默认站立状态


## 开发说明

### 代码风格
- 使用类型注解
- 遵循PEP 8编码规范
- 详细的文档字符串
- 模块化设计原则

### 扩展功能
1. 添加新的动画类型：在 `PetConfig.AnimationType` 中定义
2. 添加新的心情状态：在 `PetConfig.MoodType` 中定义
3. 自定义交互行为：修改控制器中的事件处理方法

## 依赖库

- PyQt5 - GUI框架
- 其他标准库

## 版本历史

### v2.0 - 重构版本
- ✨ 新增退出动画功能
- 🔧 全面代码重构，提高可维护性
- 📝 完善类型注解和文档
- 🐛 修复多个已知问题
- ⚡ 性能优化

### v1.0 - 基础版本
- 基本的桌宠功能
- 简单的交互系统
