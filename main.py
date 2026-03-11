"""心率桥接服务 - 入口文件"""
import asyncio
import logging

from fastapi import FastAPI
import uvicorn

from config import API_HOST, API_PORT
from ble import HeartRateScanner
from api import router
import api.routes

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Heart Rate Bridge",
    description="读取心率手表广播并提供 HTTP API 查询",
    version="1.0.0"
)

# 注册路由
app.include_router(router, prefix="/api")

# 全局扫描器实例
scanner = HeartRateScanner()
api.routes.scanner = scanner  # 注入到路由模块


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时断开连接"""
    logger.info("服务关闭中...")
    await scanner.disconnect()


async def select_and_connect():
    """扫描设备并让用户选择连接"""
    print("\n正在扫描心率设备...")
    
    try:
        devices = await scanner.scan_all()
    except Exception as e:
        print(f"扫描失败: {e}")
        return False
    
    if not devices:
        print("未发现任何心率设备")
        return False
    
    print(f"\n发现 {len(devices)} 个设备:")
    for i, device in enumerate(devices, 1):
        name = device.name or "Unknown"
        print(f"  [{i}] {name} ({device.address})")
    
    # 用户选择
    while True:
        try:
            choice = input("\n请选择要连接的设备 [1-{}]: ".format(len(devices)))
            index = int(choice) - 1
            if 0 <= index < len(devices):
                break
            print(f"请输入 1 到 {len(devices)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n已取消")
            return False
    
    # 连接设备
    selected_device = devices[index]
    device_name = selected_device.name or "Unknown"
    print(f"\n正在连接 {device_name}...")
    
    try:
        await scanner.connect(device_address=selected_device.address)
        print(f"✓ 已连接: {device_name}")
        return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


async def run_app():
    """运行应用（在同一事件循环中）"""
    print("=" * 50)
    print("  Heart Rate Bridge - 心率桥接服务")
    print("=" * 50)
    
    # 扫描并选择设备
    if not await select_and_connect():
        print("\n启动失败，请检查设备后重试")
        return
    
    # 启动 API 服务
    print(f"\nAPI 服务已启动: http://localhost:{API_PORT}")
    print(f"API 文档: http://localhost:{API_PORT}/docs")
    print("按 Ctrl+C 停止服务\n")
    
    config = uvicorn.Config(app, host=API_HOST, port=API_PORT)
    server = uvicorn.Server(config)
    await server.serve()


def main():
    """主入口"""
    try:
        asyncio.run(run_app())
    except KeyboardInterrupt:
        print("\n服务已停止")


if __name__ == "__main__":
    main()
