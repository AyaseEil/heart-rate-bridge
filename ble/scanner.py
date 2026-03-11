"""BLE 心率扫描器"""
import asyncio
import logging
from typing import Optional, Callable
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

import config
from .parser import parse_heart_rate

logger = logging.getLogger(__name__)


class HeartRateScanner:
    """心率设备扫描器"""
    
    def __init__(self):
        self.current_heart_rate: int = 0
        self.current_rr_interval: Optional[int] = None
        self.device: Optional[BLEDevice] = None
        self.client: Optional[BleakClient] = None
        self.is_connected: bool = False
        self._on_heart_rate_update: Optional[Callable[[int], None]] = None
        self.discovered_devices: list[BLEDevice] = []  # 存储发现的设备
    
    def set_callback(self, callback: Callable[[int], None]):
        """设置心率更新回调函数"""
        self._on_heart_rate_update = callback
    
    def _notification_handler(self, sender, data: bytearray):
        """处理心率通知"""
        heart_rate, _, rr_interval = parse_heart_rate(data)
        self.current_heart_rate = heart_rate
        self.current_rr_interval = rr_interval
        
        logger.info(f"心率更新: {heart_rate} bpm")
        
        if self._on_heart_rate_update:
            self._on_heart_rate_update(heart_rate)
    
    async def scan_all(self) -> list[BLEDevice]:
        """扫描所有心率设备"""
        logger.info("正在扫描心率设备...")
        self.discovered_devices = []
        
        def detection_callback(device: BLEDevice, advertisement_data):
            """检测到设备时的回调"""
            # 检查设备名称是否匹配（如果配置了）
            if config.TARGET_DEVICE_NAME and device.name != config.TARGET_DEVICE_NAME:
                return
            
            # 检查是否支持心率服务
            service_uuids = advertisement_data.service_uuids or []
            has_heart_rate_service = any(
                uuid.lower() == config.HEART_RATE_SERVICE_UUID.lower()
                for uuid in service_uuids
            )
            
            if not has_heart_rate_service:
                return
            
            # 检查是否已存在
            for existing in self.discovered_devices:
                if existing.address == device.address:
                    return
            
            # 添加到发现列表
            self.discovered_devices.append(device)
            logger.info(f"发现设备: {device.name or 'Unknown'} ({device.address})")
        
        scanner = BleakScanner(detection_callback)
        
        try:
            await scanner.start()
            await asyncio.sleep(config.BLE_SCAN_TIMEOUT)
        finally:
            await scanner.stop()
        
        if not self.discovered_devices:
            logger.warning("未发现心率设备")
        
        return self.discovered_devices
    
    async def connect(self, device_address: Optional[str] = None):
        """连接到心率设备
        
        Args:
            device_address: 设备 MAC 地址，如果为 None 则连接第一个发现的设备
        """
        # 如果已连接，先断开
        if self.is_connected:
            await self.disconnect()
        
        # 如果提供了 MAC 地址，从已发现的设备中查找
        if device_address:
            for device in self.discovered_devices:
                if device.address.lower() == device_address.lower():
                    self.device = device
                    break
            else:
                # 未找到，尝试直接用地址连接
                self.device = BLEDevice(address=device_address, name=None, details={}, rssi=-100)
        
        # 如果没有指定设备，尝试扫描
        elif not self.device:
            devices = await self.scan_all()
            if devices:
                self.device = devices[0]
        
        if not self.device:
            raise RuntimeError("未找到心率设备")
        
        logger.info(f"正在连接设备: {self.device.name or 'Unknown'} ({self.device.address})")
        
        self.client = BleakClient(self.device)
        await self.client.connect()
        self.is_connected = True
        
        logger.info("设备已连接")
        
        # 订阅心率通知
        try:
            await self.client.start_notify(
                config.HEART_RATE_MEASUREMENT_UUID,
                self._notification_handler
            )
            logger.info("已订阅心率通知")
        except Exception as e:
            logger.warning(f"订阅心率通知失败: {e}，设备可能不支持标准心率服务")
    
    async def disconnect(self):
        """断开连接"""
        if self.client and self.is_connected:
            try:
                await self.client.stop_notify(config.HEART_RATE_MEASUREMENT_UUID)
            except Exception:
                pass
            await self.client.disconnect()
            self.is_connected = False
            logger.info("设备已断开")
    
    def get_status(self) -> dict:
        """获取设备状态"""
        return {
            "connected": self.is_connected,
            "device_name": self.device.name if self.device else None,
            "device_address": self.device.address if self.device else None,
            "current_heart_rate": self.current_heart_rate,
        }
