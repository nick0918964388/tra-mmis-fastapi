import asyncio
from batch_jobs import sync_train_formation_data
import sys

async def test_sync(trainno: str = None):
    """測試同步功能"""
    try:
        print("開始同步車次編組資料...")
        await sync_train_formation_data(trainno)
    except Exception as e:
        print(f"同步失敗: {str(e)}")

if __name__ == "__main__":
    # 從命令行參數獲取車次號碼（如果有的話）
    trainno = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(test_sync(trainno)) 