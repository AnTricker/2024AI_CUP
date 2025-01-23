# %%
### 4 features
### 10minsAVG
### 72 forecastStep

import csv
import os
from datetime import datetime, timedelta

# 題目 CSV 檔案為 'questions.csv'
questions_file = 'upload(date-locationCode).csv'

# LnTrain_AVG.csv 檔案 資料夾
data_folder = '../TrainingData_Combined/10mins_AVG/'

# 輸出文件
output_file = 'An_TestData/4features_10minsAVG_72foreStep.csv'

# 讀取原始的題目 CSV 文件
with open(questions_file, newline='') as qfile:
    reader = csv.DictReader(qfile)
    questions = list(reader)

# 儲存查詢結果的列表
output_data = []

# 時間範圍：當天 07:00:00 到 08:50:00 和前一天 09:00:00 到 16:50:00
start_time_1 = "07:00:00"
end_time_1 = "08:50:00"
start_time_2 = "07:00:00"
end_time_2 = "16:50:00"

# 成功和失敗的列表
success_list = []
failure_list = []

# 遍歷每一行問題
for question in questions:
    date_str = question['日期']
    location_code = question['Location code']

    # 格式化日期為所需格式
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    
    # 前一天的日期
    previous_day = date_obj - timedelta(days=1)
    formatted_previous_day = previous_day.strftime('%Y-%m-%d')
    

    # 根據 location_code 查找對應的資料文件
    ln_file = f"{data_folder}L{location_code}Train_AVG.csv"

    if not os.path.exists(ln_file):
        print(f"警告：{ln_file} 檔案不存在，跳過此條記錄。")
        continue

    # 讀取對應 location 的資料檔案
    with open(ln_file, newline='') as datafile:
        reader = csv.DictReader(datafile)
        found_data_for_this_question = False  # 標記是否找到符合條件的資料
        
        # 遍歷檔案中的每一筆資料
        for row in reader:
            # 檢查時間是否匹配
            time_period = row['TimePeriod']
            if time_period.startswith(formatted_date) or time_period.startswith(formatted_previous_day):  # 只關心匹配日期的時間
                # 擷取時間部分
                time_only = time_period.split(' ')[1]  # 取得 HH:MM:SS 部分

                # 檢查是否在 07:00:00 到 08:50:00 之間
                if formatted_date in time_period and start_time_1 <= time_only <= end_time_1:
                    # 擷取需要的資料
                    output_data.append([
                        location_code,
                        time_period,
                        row['Temperature(°C)'],
                        row['Humidity(%)'],
                        row['Sunlight(Lux)'],
                        row['Power(mW)']
                    ])
                    found_data_for_this_question = True
                
                # 檢查前一天的時間範圍：09:00:00 到 16:50:00
                elif formatted_previous_day in time_period and start_time_2 <= time_only <= end_time_2:
                    output_data.append([
                        location_code,
                        time_period,
                        row['Temperature(°C)'],
                        row['Humidity(%)'],
                        row['Sunlight(Lux)'],
                        row['Power(mW)']
                    ])
                    found_data_for_this_question = True

                    
        if found_data_for_this_question:
            # 若有找到資料，記錄為成功
            success_list.append([date_str, location_code, 'success'])
        else:
            # 若沒找到符合條件的資料，記錄為失敗
            failure_list.append([date_str, location_code, 'Fail to find data'])

# 將結果寫入新的 CSV 檔案
with open(output_file, mode='w', newline='') as outputfile:
    writer = csv.writer(outputfile)
    # 寫入表頭
    writer.writerow(['LocationCode', 'TimePeriod', 'Temperature(°C)', 'Humidity(%)', 'Sunlight(Lux)', 'Power(mW)'])
    
    # 寫入資料
    writer.writerows(output_data)


with open("upload_Status.csv", mode='w', newline='') as successfile:
    writer = csv.writer(successfile)
    # 寫入表頭
    writer.writerow(['日期', 'LocationCode', 'Status'])
    # 寫入成功的記錄
    writer.writerows(success_list)
    # 寫入失敗的記錄
    writer.writerows(failure_list)
    
    
print(f"結果已寫入 {output_file}")