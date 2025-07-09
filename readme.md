## the device used in this repo
* spectrometer: Highfinesse LSA2R
* power meter head: Thorlabs PM100D
* rotary stage: Thorlabs PDR1C/M
* stage controller: Thorlabs PDXC2

## reminder
* the spectrometer software is required to be running before running the code
* the power meter(Thorlabs Optical power meter) and the stage controller (Thorlabs Kinesis) may NOT required, the codes are cited from [Thorlabs/Motion_Control_Examples](https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python/Benchtop/PDXC2) and [Thorlabs/Light_Analysis_Examples](https://github.com/Thorlabs/Light_Analysis_Examples/tree/main/Python/Thorlabs%20PMxxx%20Power%20Meters/TLPMX_dll)
* it doesn't matter if PM100D returns some nan power values, the code will be normal after some times, it is a bug, but I don't know how to fix it
* pip install pythonnet, NEVER pip install clr (used in the stage controller code). 
* my pip packages are old, newer versions of requirements.txt should work as well. 

## SHG_motor_control
as u see..