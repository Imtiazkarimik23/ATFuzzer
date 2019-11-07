We provide the fundamental steps to set up some of the smartphones we use in our experiment.

The crucial requirement is to have *adb* installed on the computer! (Windows also requires to install the adb drivers)


## Huawei Nexus 6 & 6P

To configure the phone in order to use AT Commands the following steps are required:

1. Unlock *Developer options* in phone settings and enable *USB debugging*.

2. Connect the phone to the computer and run the following commands (it can be done both on Linux and Windows):
    - *adb reboot fastboot*
    - *fastboot oem config bootmode bp-tools* (**Nexus 6**)
    - *fastboot oem enable-bp-tools* (**Nexus 6P**)
    - *fastboot reboot*
    
    
    
    This will set the property *sys.usb.config* to *diag,serial_smd,rmnet_ipa,adb* and allow the userd to send AT commands through the AT interface.
    
Windows might requires to install/reinstall some of the drivers. Check the environment with the following steps:

1. On *Control Panel > Hardware and Sound > Device and Printers*, double click *Nexus 6* (*Nexus 6P*) icon. The properties window should open.

2. On the Hardware panel of the property window the following devices should be listed:
    - Android Composite ADB Interface
    - Qualcomm HS-USB Diagnostics 
    - Qualcomm HS-USB Modem
    - Qualcomm Wireless HS-USB Ethernet Adapter
    - USB Composite Devide
    
    Qualcomm Modem device is the one needed to use AT Commands. On the device's properties, Modem panel we can read which 
    *Port* is used (e.g. COM3) and the *Maximum Port Speed*.
    
    If Qualcomm Modem is not listed and only *Nexus 6* (*Nexus 6P*) is listed, one problem could be Windows drivers. In this case it is necessary to 
    unistall the drivers for all the *Nexus 6* (*Nexus 6P*) devices listed (more then one could be listed). Once the previous step is completed, reconnect the phone to 
    the computer and wait for the drivers to be automtically installed.
    
   
