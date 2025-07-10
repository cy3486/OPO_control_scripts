## how to use
* set the usb COM port in the code
* set the open/close loop mode
* set the steps/angle for the motor and run


## realization logic:
* initialization: (first frame)
* connect to the motor and determine the ports
* set to closed-loop
* second frame
* wait for the signal light wavelength input
* calculate the angle from the signal light wavelength
* move the motor to that angle

This is equivalent to passing the wavelength returned by the spectrometer to the function
The angle value calculated by the function is then passed to the motor

## todo
* add a limitation to the input wavelength
* add a stop button
* delete the old readme above, add some new introduction 