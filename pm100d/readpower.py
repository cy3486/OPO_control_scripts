from datetime import datetime
from ctypes import byref, create_string_buffer, c_bool, c_int, c_int16, c_double, c_uint32
from TLPMX import TLPMX, TLPM_DEFAULT_CHANNEL
import time

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

# 连续测量并打印
while True:
    power = c_double()
    tlPM.measPower(byref(power), TLPM_DEFAULT_CHANNEL)
    print(datetime.now(), ":", power.value, "W")
    time.sleep(1)