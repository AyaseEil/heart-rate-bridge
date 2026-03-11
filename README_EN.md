[中文文档](./README.md)

# Heart Rate Bridge

A Windows service that reads heart rate broadcasts from BLE devices and provides HTTP API for querying.

## Features

- Scan and discover BLE devices with heart rate service
- Interactive device selection
- REST API for real-time heart rate queries

## Requirements

- Windows 10/11
- Python 3.10+

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## API Endpoints

| Endpoint             | Method | Description                  |
| -------------------- | ------ | ---------------------------- |
| `/api/heartrate`     | GET    | Get current heart rate       |
| `/api/device/status` | GET    | Get device connection status |

## Example

```bash
# Get heart rate
curl http://localhost:8000/api/heartrate
# Response:
    {
        "heart_rate": 78,
        "unit": "bpm"
    }

# Get device status
curl http://localhost:8000/api/device/status
# Response:
    {
        "connected": true,
        "device_name": "HUAWEI WATCH HR-83C",
        "device_address": "E4:3D:0E:0B:F8:3C",
        "current_heart_rate": 78
    }
```

## Usage

A plugin for [LiteMonitor](https://github.com/Diorser/LiteMonitor) that integrates heart rate data into the monitoring system.

### How to Use

Copy the `HeartRate.json` file from the project root directory to `LiteMonitor\resources\plugins`, then restart `LiteMonitor`.

If you want to develop your own plugins, please refer to the [LiteMonitor Plugin Development Guide](https://github.com/Diorser/LiteMonitor/blob/master/resources/plugins/PLUGIN_DEV_GUIDE.md).

If you encounter any bugs, feel free to submit an [Issue](https://github.com/AyaseEil/heart-rate-bridge/issues).

## Roadmap

1. Auto-reconnect

2. Change return value when device disconnects

## License

MIT
