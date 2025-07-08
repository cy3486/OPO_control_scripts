import pandas as pd

# 读取原始数据
df = pd.read_csv('data.csv')

# 取出Wavelength(nm)这一列
wavelength = df['Wavelength(nm)']

# 计算相邻差值（第n+1行减第n行）
wavelength_diff = wavelength.diff().fillna(0)  # 第一行没有前一项，填0

# 生成新DataFrame，只保留Wavelength和差值
result = pd.DataFrame({
    'Wavelength(nm)': wavelength,
    'Delta_Wavelength(nm)': wavelength_diff
})

# 保存到新csv
result.to_csv('wavelength_diff.csv', index=False)