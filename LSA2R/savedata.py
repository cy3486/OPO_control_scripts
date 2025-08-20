######################################################################################################
# @file AnalysisDataDemo.py
# @copyright HighFinesse GmbH.
# @version 0.1
# Homepage: http://www.highfinesse.com/
#

# MIND this please !! 
# this file plots the specrum data from the spectrometer and saves the data to a .csv file
# if you are not satisfy to the result, you can close the plot window and the script generates a new plot and flush the data to the csv file
# else, if the data satisfy you, disrrupt the script by pressing Ctrl+C in the terminal, and find the saved data in the saved_data.csv file

import sys
import ctypes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import norm

# wlmData.dll related imports
import wlmData
import wlmConst

#########################################################
# Set the DLL_PATH variable according to your environment
#########################################################
# When using the networked wlmData.dll, put this script in the same path where you put the wlmData.dll or specify the full path.
DLL_PATH = "wlmData.dll"

# Load DLL from DLL_PATH
try:
    wlmData.LoadDLL(DLL_PATH)
except:
    sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)

# Checks the number of LSA server instance(s)
if wlmData.dll.GetWLMCount(0) == 0:
    sys.exit("There is no running wlmServer instance(s).")

# Enable analysis mode
wlmData.dll.SetAnalysisMode(True)

# Enable analysis data export.
wlmData.dll.SetAnalysis(wlmConst.cSignalAnalysis, wlmConst.cAnalysisEnable)



# Set up WaitForWLMEvent mechanism
ret = wlmData.dll.Instantiate(wlmConst.cInstNotification, wlmConst.cNotifyInstallWaitEventEx, -1, 0)
if ret <= 0:
    sys.exit(f'Instantiate failed returning {ret}')
# Fetch live data from LSA
ver = ctypes.c_int32()
mode = ctypes.c_int32()
intval = ctypes.c_int32()
dblval = ctypes.c_double()
res1 = ctypes.c_int32()
    
    
while not mode.value == wlmConst.cmiPatternAnalysisWritten:
    print("waiting")
    ret = wlmData.dll.WaitForWLMEventEx(ver, mode, intval, dblval, res1)
    continue
    # Request analysis data parameters (these don't change later).
analysis_item_size = wlmData.dll.GetAnalysisItemSize(wlmConst.cSignalAnalysis)

analysis_item_count = wlmData.dll.GetAnalysisItemCount(wlmConst.cSignalAnalysis)
analysis_item_count = wlmData.dll.GetAnalysisItemCount(wlmConst.cSignalAnalysis)

if analysis_item_size == 4:
        analysis_x = (ctypes.c_float * analysis_item_count)()
        analysis_y = (ctypes.c_float * analysis_item_count)()
elif analysis_item_size == 8:
        analysis_x = (ctypes.c_double * analysis_item_count)()
        analysis_y = (ctypes.c_double * analysis_item_count)()
else:
        sys.exit("Unknown analysis data format %d" % analysis_item_size)


while True:
    ret = wlmData.dll.WaitForWLMEventEx(ver, mode, intval, dblval, res1)
    if ret <= 0:
        continue
    if mode.value == wlmConst.cmiPatternAnalysisWritten:
        # Request analysis data.
        wlmData.dll.GetAnalysisData(wlmConst.cSignalAnalysisX, analysis_x)
        wlmData.dll.GetAnalysisData(wlmConst.cSignalAnalysisY, analysis_y)
        peak_ind, _ = find_peaks(analysis_y, 0.01)
        
        npanalysis_x=np.array(analysis_x)
        npanalysis_y=np.array(analysis_y)

        # Update plot.
        # plt.clf()
        # plt.plot()
        # plt.plot(npanalysis_x, npanalysis_y)
        # plt.plot(npanalysis_x[peak_ind], npanalysis_y[peak_ind], 'x')
        # plt.pause(0.01) # update frame
        
        #将数据转换为 DataFrame
        data = pd.DataFrame({
            "Wavelength (nm)": npanalysis_x,
            "Intensity": npanalysis_y
        })                
        # Write to CSV file
        data.to_csv("saved_data.csv", index=False)
        print("data saved to saved_data.csv")

        # Read alldata.csv file
        data = pd.read_csv('saved_data.csv')

    
        # chanve to the actual data name
        x = data['Wavelength (nm)']
        y = data['Intensity (a. u.)']

        # peak_ind, _ = find_peaks(y, 0.01)

        plt.plot(x, y, 'b-', label='data')
        # plt.plot(x[peak_ind], y[peak_ind], 'o')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Intensity')
        plt.title('Signal spectrom of OPO')
        plt.legend()
        plt.grid(True)
        plt.show()