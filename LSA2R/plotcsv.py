import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from scipy.signal import find_peaks

# read alldata.csv file
# data = pd.read_csv('saved_data.csv')
data = pd.read_csv('etalon2.csv')  # change to your actual file name

# suppose etalon2.csv has two columns, 'x' and 'y'
x = data['Wavelength (nm)']
y = data['Intensity']

# 定义高斯函数
def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / (2*wid**2))

# amp = 0.58
# cen = 748.15
# wid = 0.008
# fwhm = 2 * np.sqrt(2 * np.log(2)) * wid
# print(fwhm)

peak_ind, _ = find_peaks(y, 0.01)

plt.plot(x, y, 'b-', label='data')
# plt.plot(x[peak_ind], y[peak_ind], 'o')
# plt.plot(x, gaussian(x, amp, cen, wid), 'r-', label='fit')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Intensity')
plt.title('Signal spectrom of 532 OPO at 720 nm')
plt.legend()
plt.grid(True)
plt.show()