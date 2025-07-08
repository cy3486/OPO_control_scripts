"""
scan the BBO motor while plotting and recordding: 
1. time
2. step location
3. wavelength
4. frequency
5. linewidth
6. power
and save to csv
"""
import sys
import os
import time
import csv
import ctypes
from ctypes import byref, create_string_buffer, c_bool, c_int, c_int16, c_double, c_uint32
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import norm
from datetime import datetime
import clr      # pip install pythonnet, NEVER pip install clr

## user settings
#### scan setting
target_pos = 2000
step  = 2
sleeptime = 0.5
serial_no = str("*********")  # Replace this line with your device's serial number
csv_filename = "data.csv"

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
# 查找设备
tlPM = TLPMX()
deviceCount = c_uint32()
tlPM.findRsrc(byref(deviceCount))
if deviceCount.value == 0:
    print("未找到功率计设备")
    exit(1)

resourceName = create_string_buffer(1024)
tlPM.getRsrcName(c_int(0), resourceName)
tlPM.open(resourceName, c_bool(True), c_bool(True))

# 设置参数
tlPM.setWavelength(c_double(632.5), TLPM_DEFAULT_CHANNEL)
tlPM.setPowerAutoRange(c_int16(1), TLPM_DEFAULT_CHANNEL)# int16(1) -> 自动范围启用
tlPM.setPowerUnit(c_int16(0), TLPM_DEFAULT_CHANNEL)# int16(0) -> 功率单位设置为瓦特


# init variables
times = []
position = []
wavelengths = []
frequencies = []
linewidths = []
powers = []

write_header = not os.path.exists(csv_filename)
csvfile = open(csv_filename, "a", newline='')
csvwriter = csv.writer(csvfile)
if write_header:
    csvwriter.writerow(["Time(s)", "Position", "Wavelength(nm)", "Frequency(THz)", "Linewidth(THz)", "Power(W)"])

plt.ion()  # 打开交互模式
fig, axs = plt.subplots(5, 1, figsize=(8, 10), sharex=True)
lines = []
for ax, ylabel in zip(axs, ['Position (steps)', 'Wavelength (nm)', 'Frequency (THz)', 'Linewidth (THz)', 'Power (W)']):
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
        Power = c_double()
        tlPM.measPower(byref(Power), TLPM_DEFAULT_CHANNEL)
        Power = Power.value

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
        powers.append(Power)
           
        csvwriter.writerow([t, pos, Wavelength, Frequency, Linewidth, Power])
        csvfile.flush()  # 及时写入磁盘

        # time.sleep(0.1)

        # 更新曲线数据
        data_list = [position, wavelengths, frequencies, linewidths, powers]
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
