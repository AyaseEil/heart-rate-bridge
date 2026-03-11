# Heart Rate Bridge | 心率桥接服务

一个在 Windows 上读取心率手表蓝牙广播并提供 HTTP API 查询的服务。

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
# 返回: {"heart_rate": 75, "unit": "bpm"}

# 获取设备状态
curl http://localhost:8000/api/device/status
```

## 许可证

MIT
