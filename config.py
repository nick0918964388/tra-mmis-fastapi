# API 配置
API_BASE_URL = "https://192.168.36.11/maximo/oslc/script"
HEADERS = {
    "maxauth": "TUFYX05JQ0s6Y2RlM3ZmUjQ="
}

# API 端點
ENDPOINTS = {
    "get_inv_balances": f"{API_BASE_URL}/ZZ_ITEM_GETINVB",
    "get_item": f"{API_BASE_URL}/ZZ_ITEM_GETITEM",
    "get_trans": f"{API_BASE_URL}/ZZ_ITEM_GETTRANS",
    "get_car_statement": f"{API_BASE_URL}/ZZ_CAR_STATEMENT"
}
