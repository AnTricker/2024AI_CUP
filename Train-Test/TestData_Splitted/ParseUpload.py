# %%

import pandas as pd

# 假設測試的CSV檔案路徑
input_file = 'upload(no answer).csv'  # 請修改為你的CSV檔案路徑
output_file = 'upload(parsed).csv'  # 輸出檔案

# 讀取CSV文件
data = pd.read_csv(input_file)

# 提取年月日和Location code
dates = []  # 用來存放所有的日期
location_codes = []  # 用來存放所有的Location code

# 解析每行的序號
for index, row in data.iterrows():
    test_id = str(row['序號'])  # 序號
    date = test_id[:8]  # 取前8個字元為年月日
    location_code = test_id[12:14]  # 取倒數兩個字元為Location code
    
    
    dates.append(date)
    location_codes.append(location_code)

# 創建DataFrame並去重
result = pd.DataFrame({'日期': dates, 'Location code': location_codes})

# 去除重複的 (日期, Location code) 組合
unique_result = result.drop_duplicates(subset=['日期', 'Location code'])



# 儲存為新的CSV文件
unique_result.to_csv(output_file, index=False, encoding='utf-8')

print(f"處理完成，結果已儲存為 {output_file}")