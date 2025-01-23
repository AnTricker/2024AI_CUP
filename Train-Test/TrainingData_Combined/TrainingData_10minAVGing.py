#%%

import pandas as pd
import os

# 設定資料夾路徑
input_dir = 'per_min'   # 儲存原始資料的資料夾
output_dir = '10mins_AVG'  # 儲存處理後結果的資料夾

# 確保輸出資料夾存在
os.makedirs(output_dir, exist_ok=True)

# 遍歷檔案 L1_Train.csv 到 L17_Train.csv
for i in range(1, 18):  # 從 1 到 17
    # 生成檔案名稱
    input_file = os.path.join(input_dir, f'L{i}_Train.csv')
    
    # 讀取 CSV 檔案
    data = pd.read_csv(input_file)

    # 轉換 DateTime 欄位為 datetime 格式
    data['DateTime'] = pd.to_datetime(data['DateTime'])
    
    # 創建 10 分鐘的時間區間
    data['TimePeriod'] = data['DateTime'].dt.floor('10T')

    # 按 LocationCode 和 TimePeriod 分組，並計算每組的平均值
    grouped = data.groupby(['LocationCode', 'TimePeriod']).agg({
        'WindSpeed(m/s)': 'mean',
        'Pressure(hpa)': 'mean',
        'Temperature(°C)': 'mean',
        'Humidity(%)': 'mean',
        'Sunlight(Lux)': 'mean',
        'Power(mW)': 'mean'
    }).reset_index()

    # 四捨五入每個欄位的小數位數
    grouped = grouped.round({
        'WindSpeed(m/s)': 2,
        'Pressure(hpa)': 2,
        'Temperature(°C)': 2,
        'Humidity(%)': 2,
        'Sunlight(Lux)': 2,
        'Power(mW)': 2
    })

    # 儲存處理後的結果為新的 CSV 檔案
    output_file = os.path.join(output_dir, f'L{str(i).zfill(2)}Train_AVG.csv') # 若i 是一位數，zfill(2) 也會把它補齊成兩位數（例如 8 會變成 08）。
    grouped.to_csv(output_file, index=False)

    print(f"處理結果已儲存為 '{output_file}'")
