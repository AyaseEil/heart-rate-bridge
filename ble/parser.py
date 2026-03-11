"""心率数据解析器"""


def parse_heart_rate(data: bytearray) -> int:
    """
    解析 BLE 心率测量数据
    
    Args:
        data: BLE 心率测量特征返回的原始数据
        
    Returns:
        int: 心率值 (bpm)
        
    数据格式说明:
        - 第一个字节是标志位
        - Bit 0: 心率格式 (0=UINT8, 1=UINT16)
    """
    if not data or len(data) < 2:
        return 0
    
    flags = data[0]
    
    # 解析心率值
    if flags & 0x01:
        # UINT16 格式
        if len(data) < 3:
            return 0
        return int.from_bytes(data[1:3], byteorder="little")
    else:
        # UINT8 格式
        return data[1]
