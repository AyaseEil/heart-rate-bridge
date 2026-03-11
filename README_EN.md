# Heart Rate Bridge

A Windows service that reads heart rate broadcasts from BLE devices and provides HTTP API for querying.

## Features

- Scan and discover BLE devices with heart rate service
- Interactive device selection
- REST API for real-time heart rate queries

## Requirements

- Windows 10/11
- Python 3.10+

## Installa Dependencies

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
# Response: {"heart_rate": 75, "unit": "bpm"}

# Get device status
curl http://localhost:8000/api/device/status
```

## License

MIT
