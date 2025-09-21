"""
scan the BBO motor while plotting and recordding: 
1. time
2. step location
3. wavelength
4. frequency
5. linewidth
6. power1
7. power2
and save to csv
"""
import sys
import os
import time
import csv
import ctypes
from ctypes import byref, create_string_buffer, c_bool, c_int, c_int16, c_double, c_uint32, c_char_p
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import norm
from datetime import datetime
import clr      # pip install pythonnet, NEVER pip install 
import pythoncom
pythoncom.CoInitialize()

## user settings
#### scan setting
target_pos = 40
step  = 2
sleeptime = 0.5
serial_no = str("112426310")  # Replace this line with your device's serial number
## 355 OPO 112508985
## 532 OPO 112426310
csv_filename = "532_scan_data.csv"

# power meter begin
from TLPMX import TLPMX, TLPM_DEFAULT_CHANNEL
# power meter end
# spectrum analyzer begin
import wlmData
import wlmConst
# spectrum analyzer end

# motor begin
# Add References to .NET libraries
current_dir = os.path.dirname(os.path.abspath(__file__))  # get current path in .py
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.Benchtop.PiezoCLI.dll"))
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.DeviceManagerCLI.dll"))
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.GenericPiezoCLI.dll"))
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.Benchtop.PiezoCLI import *
from Thorlabs.MotionControl.Benchtop.PiezoCLI.PDXC2 import *
from Thorlabs.MotionControl.GenericPiezoCLI.Piezo import *
# motor end

## guangpuyi
DLL_PATH = "wlmData.dll"
try:
    wlmData.LoadDLL(DLL_PATH)
except:
    sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)
if wlmData.dll.GetWLMCount(0) == 0:
    print("There is no running wlmServer instance(s).")
    sys.exit(1)

## powermeter
# 查找设备数量
tlPM = TLPMX()
deviceCount = c_uint32()
tlPM.findRsrc(byref(deviceCount))
resourceName = create_string_buffer(1024)
pm_names = []
for i in range(0, deviceCount.value):
    tlPM.getRsrcName(c_int(i), resourceName)
    pm_names.append(c_char_p(resourceName.raw).value)
    print("Resource name of device", i, ":", pm_names[i])

meters = []
for name in pm_names:
    meter = TLPMX()
    meter.open(name, c_bool(True), c_bool(True))
    meters.append(meter)



# init variables
times = []
position = []
wavelengths = []
frequencies = []
linewidths = []
power1 = []
power2 = []

write_header = not os.path.exists(csv_filename)
csvfile = open(csv_filename, "a", newline='')
csvwriter = csv.writer(csvfile)
if write_header:
    csvwriter.writerow(["Time(s)", "Position", "Wavelength(nm)", "Frequency(THz)", "Linewidth(THz)", "Power1(W)", "Power2(W)"])

plt.ion()  # 打开交互模式
fig, axs = plt.subplots(6, 1, figsize=(8, 10), sharex=True)
lines = []
for ax, ylabel in zip(axs, ['Position (steps)', 'Wavelength (nm)', 'Frequency (THz)', 'Linewidth (THz)', 'Power1 (W)', 'Power2 (W)']):
    line, = ax.plot([], [])
    ax.set_ylabel(ylabel)
    lines.append(line)
axs[-1].set_xlabel('Time (s)')
plt.tight_layout()

try:
    # init begin    
    # Uncomment this line if you are using Simulations
    # SimulationManager.Instance.InitializeSimulations()
    # Build device list so that the library can find yours
    DeviceManagerCLI.BuildDeviceList()
    # create new device
    # serial_no = str("112426310")  # Replace this line with your device's serial number
    device = InertiaStageController.CreateInertiaStageController(serial_no)
    # Connect, begin polling, and enable
    device.Connect(serial_no)
    time.sleep(0.5)
    device.StartPolling(250) #250ms polling rate
    time.sleep(0.5)  # wait statements are important to allow settings to be sent to the device
    device.EnableDevice()
    time.sleep(0.5)  # Wait for device to enable

    # Get Device information
    deviceInfo = device.GetDeviceInfo()
    print(deviceInfo.Description)
    # Wait for Settings to Initialise
    if not device.IsSettingsInitialized():
        device.WaitForSettingsInitialized(10000)  # 10 second timeout
        assert device.IsSettingsInitialized() is True
    #Get Device Configuration
    pdxc2Configuration = device.GetPDXC2Configuration(serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
    #Not used directly in example but illustrates how to obtain device settings
    currentDeviceSettings = PDXC2Settings.GetSettings(pdxc2Configuration)
    time.sleep(1)
    # init end
    #Set the open loop move paramaters for the PDXC2
    device.SetPositionControlMode(PiezoControlModeTypes.OpenLoop) # set to openloop mode
    openLoopPosition = 0
    openLoopParams = OpenLoopMoveParams()  #  create a object
    
    start_time = time.time()
      
    device.Home(5000)
    print("Homed")
    while abs(openLoopPosition) < abs(target_pos):
        openLoopParams.StepSize = openLoopPosition + step
        device.SetOpenLoopMoveParameters(openLoopParams)

        #Move the stage      
        device.MoveStart()
        openLoopPosition = openLoopPosition + step            
        print("Moving the device to ", openLoopPosition)
        #check if the stage stops ??
        pos = device.GetCurrentPosition()

        ## power
        power_values = []
        for meter in meters:
            power = c_double()
            meter.measPower(byref(power), TLPM_DEFAULT_CHANNEL)
            power_values.append(power.value)
        power1_val = power_values[0] if len(power_values) > 0 else None
        power2_val = power_values[1] if len(power_values) > 1 else None

        ## 
        t = time.time() - start_time
        Frequency = wlmData.dll.GetFrequency(0.0)
        Wavelength = wlmData.dll.GetWavelength(0.0)
        Linewidth = wlmData.dll.GetLinewidth(0, 0)

        # flush data
        times.append(t)
        position.append(openLoopPosition)
        frequencies.append(Frequency)
        wavelengths.append(Wavelength)
        linewidths.append(Linewidth)
        power1.append(power1_val)
        power2.append(power2_val)

        csvwriter.writerow([t, pos, Wavelength, Frequency, Linewidth, power1_val, power2_val])
        csvfile.flush()  # 及时写入磁盘

        # time.sleep(0.1)

        # 更新曲线数据
        data_list = [position, wavelengths, frequencies, linewidths, power1_val, power2_val]
        for line, data in zip(lines, data_list):
            line.set_data(times, data)
        for ax in axs:
            ax.relim()
            ax.autoscale_view()
        plt.pause(sleeptime)

        while (pos != device.GetCurrentPosition()):
            pos = device.GetCurrentPosition()
            device.StopPolling()
        time.sleep(sleeptime) # this loop end
   # Disconnect the Device    
    device.Disconnect(True)
except Exception as e:
    print(e)

# Uncomment this line if you are using Simulations
# SimulationManager.Instance.UninitializeSimulations()
