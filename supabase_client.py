from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def determine_car_type(group_name: str) -> str:
    """判斷車種類型"""
    # 使用正則表達式檢查是否以日期格式開頭 (yyyy/mm/dd)
    date_pattern = r'^\d{4}/\d{2}/\d{2}'
    if re.match(date_pattern, group_name):
        return "客車車身"
    return "動力車頭"

async def insert_train_formation_data(formation_data: dict):
    """插入車次編組數據到 Supabase"""
    try:
        print(f"接收到的資料結構: {formation_data}")
        total_cars = 0
        for statement in formation_data.get('statementlist', []):
            try:
                print(f"處理的 statement 資料: {statement}")
                
                # 檢查必要欄位
                if 'group' not in statement:
                    print(f"缺少 'group' 欄位，完整的 statement: {statement}")
                    continue
                
                # 判斷車種類型
                formation_type = determine_car_type(statement['group'])
                
                formation = {
                    'trainno': statement.get('trainno', ''),
                    'transdate': statement.get('transdate', ''),
                    'group_name': statement['group'],
                    'formation_type': formation_type,
                    'sync_time': datetime.now().isoformat()
                }
                
                print(f"\n準備寫入編組資料: {formation}")
                formation_response = supabase.table('train_formations').upsert(formation).execute()
                print(f"編組寫入結果: {formation_response}")
                
                formation_id = formation_response.data[0]['id']
                
                cars = []
                for car in statement.get('carlist', []):
                    car_data = {
                        'train_formation_id': formation_id,
                        'assetnum': car.get('assetnum', ''),
                        'trainseq': car.get('trainseq', 0),
                        'car_type': formation_type,
                        'sync_time': datetime.now().isoformat()
                    }
                    cars.append(car_data)
                
                if cars:
                    print(f"準備寫入車輛資料: {cars}")
                    cars_response = supabase.table('train_cars').upsert(cars).execute()
                    print(f"車輛資料寫入結果: {cars_response}")
                    print(f"  - 車輛清單: {', '.join([car['assetnum'] for car in cars])}")
                    print(f"  - 編組類型: {formation_type}")
                    print(f"  - 更新 {len(cars)} 筆車輛資料")
                    total_cars += len(cars)
                    
            except Exception as inner_e:
                print(f"處理單筆資料時發生錯誤: {str(inner_e)}")
                print(f"錯誤的資料內容: {statement}")
                continue
                
        print(f"\n總計更新 {total_cars} 筆車輛資料")
        return True
    except Exception as e:
        print(f"資料庫寫入錯誤: {str(e)}")
        print(f"完整的錯誤信息: ", e)
        print(f"錯誤的資料結構: {formation_data}")
        raise

async def insert_items_data(items_data: list):
    """插入物料數據到 Supabase"""
    try:
        response = supabase.table('items').upsert(items_data).execute()
        return response
    except Exception as e:
        print(f"Error inserting items data: {str(e)}")
        raise

async def insert_inventory_data(inventory_data: list):
    """插入庫存數據到 Supabase"""
    try:
        response = supabase.table('inventory').upsert(inventory_data).execute()
        return response
    except Exception as e:
        print(f"Error inserting inventory data: {str(e)}")
        raise