from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from api_utils import make_api_request
from config import HEADERS, ENDPOINTS
from datetime import date
from batch_jobs import setup_scheduler, sync_train_formation_data

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """應用程序啟動時啟動排程器"""
    scheduler = setup_scheduler()
    scheduler.start()

@app.get("/getinvbalances")
async def get_inv_balances(itemnum: Optional[str] = Query(None), description: Optional[str] = Query(None)):
    if not itemnum and not description:
        raise HTTPException(status_code=400, detail="必須提供 itemnum 或 description 參數")
    
    query_param = f"itemnum={itemnum}" if itemnum else f"description={description}"
    url = f"{ENDPOINTS['get_inv_balances']}?{query_param}"
    
    return await make_api_request(url, HEADERS)

@app.get("/getitem")
async def get_item(itemnum: Optional[str] = Query(None), description: Optional[str] = Query(None)):
    if not itemnum and not description:
        raise HTTPException(status_code=400, detail="必須提供 itemnum 或 description 參數")
    
    query_param = f"itemnum={itemnum}" if itemnum else f"description={description}"
    url = f"{ENDPOINTS['get_item']}?{query_param}"
    
    return await make_api_request(url, HEADERS)

@app.get("/gettrans")
async def get_trans(
    itemnum: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    trans_type: Optional[str] = Query(None, description="異動類型"),
    start_date: Optional[date] = Query(None, description="單據日期起始"),
    end_date: Optional[date] = Query(None, description="單據日期結束"),
    dept: Optional[str] = Query(None, description="單位"),
    work_order: Optional[str] = Query(None, description="工作號"),
    warehouse: Optional[str] = Query(None, description="倉庫"),
    vehicle_number: Optional[str] = Query(None, description="車號")
):
    query_params = {
        "itemnum": itemnum,
        "description": description,
        "transtype": trans_type,
        "startdate": start_date,
        "enddate": end_date,
        "dept": dept,
        "workorder": work_order,
        "warehouse": warehouse,
        "vehiclenumber": vehicle_number
    }
    
    # 計算非空參數的數量
    non_empty_params = sum(1 for value in query_params.values() if value is not None)
    
    if non_empty_params < 3:
        raise HTTPException(status_code=400, detail="必須提供至少3個查詢參數")
    
    # 構建查詢字符串
    query_string = "&".join(f"{key}={value}" for key, value in query_params.items() if value is not None)
    
    url = f"{ENDPOINTS['get_trans']}?{query_string}"
    
    return await make_api_request(url, HEADERS)

@app.post("/sync/train-formation")
async def manual_sync_train_formation(trainno: Optional[str] = Query(None)):
    """手動觸發車次編組同步"""
    try:
        await sync_train_formation_data(trainno)
        if trainno:
            return {"status": "success", "message": f"車次 {trainno} 編組同步完成"}
        else:
            return {"status": "success", "message": "所有車次編組同步完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
