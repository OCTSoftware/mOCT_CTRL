# mOCT_CTRL

Control software for the focus piezo and reference stage. \
All settings are made in Config.txt **before** the program starts.

### Select devices

True or False

> USING_MIPOS = True \
> USING_KCUBE = True

**NIDAQ board device and ports**

> NIDAQ_DEVICE = Dev2 \
> NIDAQ_AO_PORT = ao0 \
> NIDAQ_AI_PORT = ai0

**Thorlabs KCube serial number**

> KCUBE_SN = 28252775

**StepSize**

> KCUBE_STEPSIZE = 0.1

**Slider position for dedicated microscope objectiv lenses**

> zero  =  0.0 \
> 05x16 = 10.0 \
> 10x03 = 20.0 \
> 20x05 = 30.0 \
> 40x08 = 40.0

![Screenshot from the GUI](GUI.png)

https://stackoverflow.com/questions/71226142/pyinstaller-with-nidaqmx
