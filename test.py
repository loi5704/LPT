import pandas as pd
import sys

# Thay đổi encoding mặc định
sys.stdout.reconfigure(encoding='utf-8')

dataframe = pd.read_excel('./uploads/Data_final.xlsx')
data_preview=dataframe[:100].to_string()
# Tính số token của dữ liệu
data_token_count = len(dataframe.to_string().split())

print(data_token_count)