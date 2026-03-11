"""配置文件"""

# BLE 配置
BLE_SCAN_TIMEOUT = 10.0  # 扫描超时（秒）
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"  # 标准心率服务 UUID
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # 心率测量特征 UUID

# 目标设备名称（可选，为空则连接第一个发现的心率设备）
TARGET_DEVICE_NAME = ""  # 例如: "MI Band 7", "Apple Watch" 等

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000
