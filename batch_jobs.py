from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, date
import os
from dotenv import load_dotenv
from api_utils import make_api_request
from config import HEADERS, ENDPOINTS
from supabase_client import insert_items_data, insert_inventory_data, insert_train_formation_data

load_dotenv()

async def sync_train_formation_data(trainno: str = None):
    """同步車次編組資料"""
    try:
        today = date.today().strftime("%Y-%m-%d")
        
        # 構建 URL
        url = f"{ENDPOINTS['get_car_statement']}?transdate={today}"
        if trainno:
            url += f"&trainno={trainno}"
            print(f"\n=== 開始同步 {today} 車次{trainno} 編組資料 ===")
        else:
            print(f"\n=== 開始同步 {today} 所有車次編組資料 ===")
        
        print(f"正在從 API 獲取資料...")
        
        formation_data = await make_api_request(url, HEADERS)
        
        if not formation_data or 'statementlist' not in formation_data:
            print("API 回應資料格式不正確或為空")
            raise ValueError("API 回應資料格式不正確或為空")
        
        statement_count = len(formation_data.get('statementlist', []))
        print(f"收到 {statement_count} 個編組資料")
            
        result = await insert_train_formation_data(formation_data)
        
        if trainno:
            print(f"=== 同步完成: {today} 車次 {trainno} ===\n")
        else:
            print(f"=== 同步完成: {today} 所有車次 ===\n")
        return result
    except Exception as e:
        print(f"同步失敗: {str(e)}")
        raise

def setup_scheduler():
    """設置排程器"""
    scheduler = AsyncIOScheduler()
    
    # 從環境變量獲取間隔時間（分鐘）
    interval_minutes = int(os.getenv('SCHEDULER_INTERVAL_MINUTES', 60))
    
    # 添加定時任務
    scheduler.add_job(
        sync_items_data,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='sync_items',
        name='Sync items data'
    )
    
    scheduler.add_job(
        sync_inventory_data,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='sync_inventory',
        name='Sync inventory data'
    )
    
    # 添加車次編組同步任務
    scheduler.add_job(
        sync_train_formation_data,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='sync_train_formation',
        name='Sync train formation data'
    )
    
    return scheduler 