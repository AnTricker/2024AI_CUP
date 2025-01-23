# %%
''' 一口氣train完17個檔案'''
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
import numpy as np
import pandas as pd
import os
from datetime import datetime

# 設定LSTM往前看的筆數和預測筆數
LookBackNum = 72  
ForecastNum = 48 

# 設定資料夾路徑
input_dir = os.getcwd() + './TrainingData_Combined/10mins_AVG'  # 訓練資料夾
output_dir = os.getcwd() + './LSTM_model/72to48'  # 儲存模型的資料夾

# 確保儲存模型的資料夾存在
os.makedirs(output_dir, exist_ok=True)

# 遍歷檔案 L01Train_AVG.csv 到 L17Train_AVG.csv
for i in range(1, 18):  # 從 1 到 17
    # 生成檔案名稱
    TestDataFile = os.path.join(input_dir, f'L{str(i).zfill(2)}Train_AVG.csv') # zfill(2) 會把i補齊成兩位數（例如 8 會變成 08）。
    
    # 讀取 CSV 檔案
    SourceData = pd.read_csv(TestDataFile, encoding='utf-8')
    
    # 設定要使用的特徵欄位
    features = ['Temperature(°C)', 'Humidity(%)', 'Sunlight(Lux)', 'Power(mW)']
    AllOutPut = SourceData[features].values  # 轉換成numpy array

    X_train = []  # 特徵 X
    y_train = []  # 標籤 y

    # 製作訓練資料
    for j in range(LookBackNum, len(AllOutPut)):  
        X_train.append(AllOutPut[j-LookBackNum:j, :])  
        y_train.append(AllOutPut[j, -1])  # 目標值是 Power(mW)

    # 轉換為numpy array
    X_train = np.array(X_train)
    print(X_train.shape)  
    y_train = np.array(y_train) 
    
    # Reshape X_train 使其符合LSTM輸入要求
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 4))  # 4個特徵
    
    
    # 建立LSTM模型
    regressor = Sequential()

    # 第一層 LSTM
    regressor.add(LSTM(units=128, return_sequences=True, input_shape=(X_train.shape[1], 4)))

    # 第二層 LSTM
    regressor.add(LSTM(units=64))

    # Dropout層，用於防止過擬合
    regressor.add(Dropout(0.2))

    # 輸出層
    regressor.add(Dense(units=4))  # 輸出4個特徵（Temperature, Humidity, Sunlight, Power）

    # 編譯模型
    regressor.compile(optimizer='adam', loss='mean_squared_error')

    # 開始訓練模型
    regressor.fit(X_train, y_train, epochs=100, batch_size=128)

    # 儲存模型
    NowDateTime = datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ")
    model_filename = os.path.join(output_dir, f'LSTM_4_L{str(i).zfill(2)}.h5')
    regressor.save(model_filename)

    print(f'Model for L{str(i).zfill(2)} has been saved as {model_filename}')


# %%
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

# 設定檔案路徑
upload_file = './TestData_Splitted/upload(date-locationCode).csv'  # 題目檔案
testdata_file = './TestData_Splitted/An_TestData/4features_10minsAVG_72foreStep.csv'  # testdata檔案
model_dir = './LSTM_model/72to48/'  # 存放 LSTM 模型的資料夾
output_dir = './output/'  # 輸出檔案的資料夾
os.makedirs(output_dir, exist_ok=True)

# 載入資料
upload_data = pd.read_csv(upload_file, encoding='utf-8')
testdata = pd.read_csv(testdata_file, encoding='utf-8')

# 確認資料型態
upload_data['日期'] = upload_data['日期'].astype(str)
upload_data['Location code'] = upload_data['Location code'].astype(str).str.zfill(2)
testdata['LocationCode'] = testdata['LocationCode'].astype(str).str.zfill(2)

# 參數
features_number = 4
LookBackNum = 72  # 每次預測所需的參考數據筆數
ForecastNum = 48  # 預測未來的筆數

# 儲存所有題目的預測結果
all_predictions = []

# 處理每一題
for idx, row in upload_data.iterrows():
    date = row['日期']
    location_code = row['Location code']

    print(f"Processing Question {idx + 1}/{len(upload_data)}: Date={date}, LocationCode={location_code}")
    
    # 轉換日期格式為 '20240117' 形式
    date_obj = datetime.strptime(date, '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    formatted_date_str = formatted_date.replace('-', '')  # '20240117'

    # 計算前一天的日期並轉換格式
    previous_day_obj = date_obj - timedelta(days=1)
    previous_day = previous_day_obj.strftime('%Y-%m-%d')
    previous_day_str = previous_day.replace('-', '')  # '20240116'

    # TimePeriod 的格式是 '2024-01-17 07:00:00'
    testdata['DatePart'] = testdata['TimePeriod'].str.split().str[0]  # 只保留 '2024-01-17'
    testdata['DatePart'] = testdata['DatePart'].str.replace('-', '')  # 轉換為 '20240117'
    
    
    #### 篩選出對應的測試資料
    question_data = testdata[
        (testdata['LocationCode'] == location_code) & 
        ((testdata['DatePart'] == formatted_date_str) | (testdata['DatePart'] == previous_day_str))
    ]

    if question_data.shape[0] < LookBackNum:
        print(question_data.shape[0])
        print(f"Warning: Not enough data for question {idx + 1}, skipping.")
        continue

    # 提取參考資料
    ReferData = question_data[['Temperature(°C)', 'Humidity(%)', 'Sunlight(Lux)', 'Power(mW)']].values

    # 載入對應的 LSTM 模型
    model_path = os.path.join(model_dir, f'LSTM_4_L{location_code}.h5')
    if not os.path.exists(model_path):
        print(f"Warning: Model for LocationCode {location_code} not found, skipping.")
        continue

    regressor = load_model(model_path)

    # 預測未來數據
    inputs = ReferData.tolist()  # 初始化輸入數據
    testD = []  # 儲存每次預測的結果
    count = 0  # 初始化計數器

    # 迴圈預測未來__(ForecastNum設定)筆數據
    for i in range(ForecastNum):
        print(f"inputs shape before merge predict: {np.array(inputs).shape}")
        if i > 0:
            print(f"PredictOutPut shape: {testD[i - 1].shape}")
            inputs = np.concatenate((inputs, testD[i - 1]), axis=0)
        print(f"inputs shape after merge predict: {np.array(inputs).shape}")

        # 切出新的參考資料12筆(往前看12筆)
        X_test = []
        X_test.append(np.array(inputs[0 + i : LookBackNum + i]))

        '''Reshaping'''
        NewTest = np.array(X_test)
        print(f"Shape of X_test before reshape: {np.array(X_test).shape}")
        NewTest = np.reshape(NewTest, (NewTest.shape[0], NewTest.shape[1], 4))

        # 使用LSTM模型進行預測
        predicted = regressor.predict(NewTest)
        print(f"predicted shape: {predicted.shape}")
        testD.append(np.round(predicted, 2))  # 將預測結果保留2位小數
        print(f"PerdictOutPut element shape: {testD[0].shape}")
        print(f"PerdictOutPut length: {len(testD)}")
        print("perdict done\n")

    # 將結果儲存
    all_predictions.append({
        'Date': date,
        'LocationCode': location_code,
        'Predictions': testD
    })

# 儲存所有預測結果為 CSV
output_file = os.path.join(output_dir, f'Predictions_{features_number}features_{LookBackNum}to{ForecastNum}.csv')
output_data = []
for prediction in all_predictions:
    for step, values in enumerate(prediction['Predictions']):
        output_data.append({
            'Date': prediction['Date'],
            'LocationCode': prediction['LocationCode'],
            'Step': step + 1,
            # 'Temperature(°C)': values[0][0],
            # 'Humidity(%)': values[0][1],
            # 'Sunlight(Lux)': values[0][2],
            'Power(mW)': round(values[0][3], 2)
        })

output_df = pd.DataFrame(output_data)
output_df.to_csv(output_file, index=False, encoding='utf-8')

print(f"All predictions saved to {output_file}")

# %%
''' 把預測出的發電量 放入上傳檔案 '''

import pandas as pd

# 假設這是包含Power欄位的DataFrame
Perdict_data = pd.read_csv('./output/Predictions_4features_72to48.csv')

# 假設 upload(no answer).csv 已經被加載
upload_df = pd.read_csv('./TestData_Splitted/upload(no answer).csv')

# 創建Power數據列表並保留2位小數
# 將 "Power(mW)" 欄位的數據轉換為數字並保留2位小數
power_values = [round(float(value), 2) for value in Perdict_data["Power(mW)"]]

# 檢查upload_df是否有足夠的行數來匹配
assert len(upload_df) == len(power_values), "行數不匹配，請檢查upload(no answer).csv檔案!"

# 將Power值填入答案欄位
upload_df['答案'] = power_values

# 儲存更新後的結果到新的CSV檔案
upload_df.to_csv('upload_4features_72to48.csv', index=False)

# 顯示結果（可選）
print(upload_df)