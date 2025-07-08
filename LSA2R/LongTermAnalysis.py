import wlmData
import wlmConst
import os
import csv
import sys
import time
import matplotlib.pyplot as plt

DLL_PATH = "wlmData.dll"
try:
    wlmData.LoadDLL(DLL_PATH)
except:
    sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)

if wlmData.dll.GetWLMCount(0) == 0:
    print("There is no running wlmServer instance(s).")
    sys.exit(1)

# 初始化数据列表
times = []
frequencies = []
temperatures = []
wavelengths = []
linewidths = []


# CSV文件准备
csv_filename = "wlm_data.csv"
write_header = not os.path.exists(csv_filename)
csvfile = open(csv_filename, "a", newline='')
csvwriter = csv.writer(csvfile)
if write_header:
    csvwriter.writerow(["Time(s)", "Frequency(THz)", "Temperature(°C)", "Wavelength(nm)", "Linewidth(nm)"])


plt.ion()  # 打开交互模式
fig, axs = plt.subplots(4, 1, figsize=(8, 8), sharex=True)
lines = []
for ax, ylabel in zip(axs, ['Frequency (THz)', 'Temperature (°C)', 'Wavelength (nm)', 'Linewidth (nm)']):
    line, = ax.plot([], [])
    ax.set_ylabel(ylabel)
    lines.append(line)
axs[-1].set_xlabel('Time (s)')
plt.tight_layout()

start_time = time.time()
while True:
    t = time.time() - start_time
    Frequency = wlmData.dll.GetFrequency(0.0)
    Temperature = wlmData.dll.GetTemperature(0.0)
    Wavelength = wlmData.dll.GetWavelength(0.0)
    Linewidth = wlmData.dll.GetLinewidth(0, 0)
    times.append(t)
    frequencies.append(Frequency)
    temperatures.append(Temperature)
    wavelengths.append(Wavelength)
    linewidths.append(Linewidth)

    # 保存到CSV
    csvwriter.writerow([t, Frequency, Temperature, Wavelength, Linewidth])
    csvfile.flush()  # 及时写入磁盘

    # 更新曲线数据
    data_list = [frequencies, temperatures, wavelengths, linewidths]
    for line, data in zip(lines, data_list):
        line.set_data(times, data)
    for ax in axs:
        ax.relim()
        ax.autoscale_view()
    plt.pause(0.01)