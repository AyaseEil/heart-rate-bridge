[English](./README_EN.md)

# Heart Rate Bridge | 心率桥接服务

一个在 Windows 上读取心率手表蓝牙广播并提供 API 查询的服务。

## 功能

- 扫描并发现支持心率服务的 BLE 设备
- 交互式选择要连接的设备
- 提供 API 查询实时心率

## 环境要求

- Windows 10/11
- Python 3.10+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## API 接口

| 端点                 | 方法 | 描述             |
| -------------------- | ---- | ---------------- |
| `/api/heartrate`     | GET  | 获取当前心率     |
| `/api/device/status` | GET  | 获取设备连接状态 |

## 示例

```bash
# 获取心率
curl http://localhost:8000/api/heartrate
# 返回:
    {
        "heart_rate": 78,
        "unit": "bpm"
    }

# 获取设备状态
curl http://localhost:8000/api/device/status
# 返回:
    {
        "connected": true,
        "device_name": "HUAWEI WATCH HR-83C",
        "device_address": "E4:3D:0E:0B:F8:3C",
        "current_heart_rate": 78
    }
```

## 用途

[LiteMonitor](https://github.com/Diorser/LiteMonitor)的一个小插件，可以把心率数据集成到监控系统中。

### 使用方法

把本项目根目录下的`HeartRate.json`放到`LiteMonitor\resources\plugins`中，然后重启 `LiteMonitor` 即可。

如果你也想开发自己的插件，可以参考[LiteMonitor 插件开发完全指南](https://github.com/Diorser/LiteMonitor/blob/master/resources/plugins/PLUGIN_DEV_GUIDE.md)。

如果遇到BUG，欢迎提出 [Issues](https://github.com/AyaseEil/heart-rate-bridge/issues)。

## 更新计划


## 开源协议

MIT
