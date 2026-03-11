"""心率数据解析器"""
from typing import Tuple, Optional


def parse_heart_rate(data: bytearray) -> Tuple[int, Optional[int], Optional[int]]:
    """
    解析 BLE 心率测量数据
    
    Args:
        data: BLE 心率测量特征返回的原始数据
        
    Returns:
        Tuple[int, Optional[int], Optional[int]]: (心率值, 能量消耗, RR间隔)
        
    数据格式说明:
        - 第一个字节是标志位
        - Bit 0: 心率格式 (0=UINT8, 1=UINT16)
        - Bit 1: 是否包含传感器接触状态
        - Bit 2: 传感器接触支持
        - Bit 3: 是否包含能量消耗
        - Bit 4: 是否包含RR间隔
    """
    if not data or len(data) < 2:
        return 0, None, None
    
    flags = data[0]
    offset = 1
    
    # 解析心率值
    heart_rate_format = flags & 0x01
    if heart_rate_format:
        # UINT16 格式
        if len(data) < offset + 2:
            return 0, None, None
        heart_rate = int.from_bytes(data[offset:offset + 2], byteorder="little")
        offset += 2
    else:
        # UINT8 格式
        heart_rate = data[offset]
        offset += 1
    
    # 解析能量消耗（如果存在）
    energy_expended = None
    if flags & 0x08:
        if len(data) >= offset + 2:
            energy_expended = int.from_bytes(data[offset:offset + 2], byteorder="little")
            offset += 2
    
    # 解析RR间隔（如果存在）
    rr_interval = None
    if flags & 0x10:
        if len(data) >= offset + 2:
            rr_interval = int.from_bytes(data[offset:offset + 2], byteorder="little")
    
    return heart_rate, energy_expended, rr_interval
