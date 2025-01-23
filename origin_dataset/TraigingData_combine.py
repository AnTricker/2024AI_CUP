#%%

''' combine Additional data'''
import pandas as pd
import os

# 設定資料夾路徑
folder_1 = '36_TrainingData'  # 存放 Ln_Train.csv 的資料夾 1
folder_2 = '36_TrainingData_Additional_V2'  # 存放額外資料的資料夾 2

# 遍歷資料夾 2 中的檔案
for filename in os.listdir(folder_2):
    if filename.startswith('L') and filename.endswith('Train_2.csv'):
        # 從檔案名稱中提取數字 n，例如 'L1Train.csv' 中的 '1'
        n = filename[1:filename.index('_')]  # 提取 'L' 後的數字部分
        print(n)

        # 構建對應的檔案路徑，資料夾 1 中的檔案
        corresponding_file = os.path.join(folder_1, f'L{n}_Train.csv')

        # 檢查對應檔案是否存在
        if os.path.exists(corresponding_file):
            # 讀取資料夾 2 中的檔案到 df1
            df1 = pd.read_csv(os.path.join(folder_2, filename))

            # 讀取資料夾 1 中的對應檔案到 df2
            df2 = pd.read_csv(corresponding_file)

            # 顯示資料檢查 (可以選擇性列印部分資料來檢查是否正確)
            print(f"檔案 {filename} 和對應的 {corresponding_file} 已讀取")
            print(f"df1 (來自 {folder_2}):\n{df1.head()}")
            print(f"df2 (來自 {folder_1}):\n{df2.head()}")
        
            # 檢查第二份檔案中的 DateTime 是否有在第一份檔案中，沒有的話就加入第一份檔案
            df2_not_in_df1 = df2[~df2['DateTime'].isin(df1['DateTime'])]
            
            # 將這些資料加入第一份檔案
            df_combined = pd.concat([df1, df2_not_in_df1], ignore_index=True)
            df_combined = df_combined.sort_values('DateTime').reset_index(drop=True)  # 對合併後的資料排序
            
            # 儲存合併後的資料到新的CSV檔案
            df_combined.to_csv(f'../Train-Test/TrainingData_Combined/per_min/L{n}_Train.csv', index=False)
  
        
        
            print("合併完成")
        else:
            print(f"對應檔案 {corresponding_file} 不存在，跳過 {filename}")
# %%
