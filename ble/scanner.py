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
        self.device: Optional[BLEDevice] = None
        self.client: Optional[BleakClient] = None
        self.is_connected: bool = False
        self._on_heart_rate_update: Optional[Callable[[int], None]] = None
        self.discovered_devices: list[BLEDevice] = []  # 存储发现的设备
        self._is_reconnecting: bool = False  # 是否正在重连
    
    def set_callback(self, callback: Callable[[int], None]):
        """设置心率更新回调函数"""
        self._on_heart_rate_update = callback
    
    def _notification_handler(self, sender, data: bytearray):
        """处理心率通知"""
        self.current_heart_rate = parse_heart_rate(data)
        
        logger.info(f"心率更新: {self.current_heart_rate} bpm")
        
        if self._on_heart_rate_update:
            self._on_heart_rate_update(self.current_heart_rate)
    
    def _disconnected_callback(self, client):
        """设备断开连接回调"""
        logger.warning(f"设备已断开: {self.device.name if self.device else 'Unknown'}")
        self.is_connected = False
        self.current_heart_rate = -1  # 断开后重置心率为 0
        
        # 触发自动重连
        if not self._is_reconnecting:
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """自动重连"""
        if self._is_reconnecting or not self.device:
            return
        
        self._is_reconnecting = True
        device_name = self.device.name or "Unknown"
        
        logger.info(f"开始尝试重连 {device_name}...")
        
        retry_count = 0
        max_retries = 10  # 最大重试次数
        
        while retry_count < max_retries:
            retry_count += 1
            logger.info(f"重连尝试 {retry_count}/{max_retries}...")
            
            try:
                # 尝试重新连接
                self.client = BleakClient(
                    self.device,
                    disconnected_callback=self._disconnected_callback
                )
                await self.client.connect()
                self.is_connected = True
                
                # 订阅心率通知
                await self.client.start_notify(
                    config.HEART_RATE_MEASUREMENT_UUID,
                    self._notification_handler
                )
                
                logger.info(f"✓ 重连成功: {device_name}")
                self._is_reconnecting = False
                return
                
            except Exception as e:
                logger.warning(f"重连失败: {e}")
                await asyncio.sleep(3)  # 等待后重试
        
        logger.error(f"重连失败，已达到最大重试次数 ({max_retries})")
        self._is_reconnecting = False
    
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
        
        self.client = BleakClient(
            self.device,
            disconnected_callback=self._disconnected_callback
        )
        
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
        self._is_reconnecting = False
        
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
            "reconnecting": self._is_reconnecting,
        }
