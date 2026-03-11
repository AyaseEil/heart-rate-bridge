"""API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ble import HeartRateScanner

router = APIRouter()

# 全局扫描器实例（在 main.py 中注入）
scanner: HeartRateScanner = None


class HeartRateResponse(BaseModel):
    """心率响应模型"""
    heart_rate: int
    unit: str = "bpm"


class DeviceStatusResponse(BaseModel):
    """设备状态响应模型"""
    connected: bool
    device_name: str | None = None
    device_address: str | None = None
    current_heart_rate: int


@router.get("/heartrate", response_model=HeartRateResponse)
async def get_heart_rate():
    """获取当前心率"""
    if not scanner:
        raise HTTPException(status_code=503, detail="扫描器未初始化")
    
    if not scanner.is_connected:
        raise HTTPException(status_code=503, detail="设备未连接")
    
    return HeartRateResponse(heart_rate=scanner.current_heart_rate)


@router.get("/device/status", response_model=DeviceStatusResponse)
async def get_device_status():
    """获取设备状态"""
    if not scanner:
        raise HTTPException(status_code=503, detail="扫描器未初始化")
    
    status = scanner.get_status()
    return DeviceStatusResponse(**status)
