# the stage move from 0 to the "target position" at a step of "step", the stage wait for "sleeptime" seconds after each step
# before each move loop, the stage is homed (initialized).
# in line 34, enter your device's serial number

import os
import time
import sys
import clr

target_pos = 100
step  = 20
sleeptime = 0.5

# Add References to .NET libraries
current_dir = os.path.dirname(os.path.abspath(__file__))  # get current path
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.Benchtop.PiezoCLI.dll"))
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.DeviceManagerCLI.dll"))
clr.AddReference(os.path.join(current_dir, "dlls", "Thorlabs.MotionControl.GenericPiezoCLI.dll"))


from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.Benchtop.PiezoCLI import *
from Thorlabs.MotionControl.Benchtop.PiezoCLI.PDXC2 import *
from Thorlabs.MotionControl.GenericPiezoCLI.Piezo import *

def main():
    # Uncomment this line if you are using Simulations
    # SimulationManager.Instance.InitializeSimulations()

    try:
        # init begin
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()
        # create new device
        serial_no = str("*********")  # Replace this line with your device's serial number
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
            time.sleep(0.1)
            while (pos != device.GetCurrentPosition()):
                pos = device.GetCurrentPosition()
                time.sleep(0.5)

            # Stop polling and close device
            device.StopPolling()
            time.sleep(sleeptime) # this loop end

        # Disconnect the Device    
        device.Disconnect(True)
    except Exception as e:
        print(e)

    # Uncomment this line if you are using Simulations
    # SimulationManager.Instance.UninitializeSimulations()
if __name__ == "__main__":
    main()