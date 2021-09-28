# Reading the Wensn WS1361 Sound Pressure Level (SPL) Meter over USB (on the Raspberry Pi)

The Wensn WS1361 is a cheap but decent quality Sound Level Meter from China. You can get it on Aliexpress for $25-30, for example here: https://www.aliexpress.com/item/32328084637.html Make sure you get the one with the USB cable or you won't be able to talk to it. (Usefully, the device can be powered over USB without batteries installed.)

![WS1361](./WS1361.png)

This Python (3) library lets you set the modes of the WS1361, and read the current sound level.

The WS1361 can read with 'A' or 'C' sound weighting, and 'fast' or 'slow' averaging. The library uses the default of 'A' and 'slow'.

You can also set the "range". This does change the range shown on the device display, but doesn't change the sound levels returned over USB. Similarly, you can set the "maxMode" to "max" or "instant", which also changes what is shown on the device display (e.g., "max" mode shows the running peak value), but doesn't change the sound levels returned over USB.

### NOTE: depending on your setup you may need to use a ground loop USB isolator
### PERMISSION: when wensn.py run as a service permissions for _logroll.py_ need to be set as well (or, if not needed, just disable)

We used the [Adafruit USB Isolator - 100mA Isolated Low/Full Speed USB](https://www.adafruit.com/product/2107). ATTENTION set the speed of the isolator to **LOW** otherwise the WS1361 will not be detected

## Step by Step Installation (Rpi Headless):

1) Once Raspberry Pi OS LITE (32-bit) is installed
    -  `sudo raspi-config`
        - change *Hostname* and *Password*
        - enable SSH
        - add WiFi connection(s)
        - reboot, check the connection and find IP address for SSH `ifconfig wlan0`
    - `sudo apt-get update`
    - `sudo apt-get upgrade`

2) Install the packages
    - `sudo apt-get install python3-pip`
        - `sudo pip3 install pyusb`
        - `sudo pip3 install paho-mqtt`
    - `sudo apt install git`

3) Clone this repository and setup the variables
    - git clone https://github.com/ucl-casa-ce/wensn.git /opt/noisemeter
    - using `sudo nano /opt/noisemeter/SPLmqtt.py`
        - change value for *USERNAME*, *PASSWORD*, *MQTT_BROKER* and its port
    - using `sudo nano /opt/noisemeter/wensn.py`
        - change the *TOPIC* at the end of the file `spl.client.publish("TOPIC", jsonString)` 

Finally, run:

```
sudo python3 wensn.py
```

## Setting permissions for the usb device:

If you find that running as your own user fails with with error, "usb.core.USBError: [Errno 13] Access denied (insufficient
permissions)", that means you have to fix your device permissions.

To do this, create a file called
"/etc/udev/rules.d/50-usb-perms.rules". The file has to end in
".rules" to be read.

Add this rule to the file:
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05dc", GROUP="plugdev", MODE="0660"
```

then run:
```
sudo udevadm control --reload ; sudo udevadm trigger
```

Make sure your user is in group plugdev:
```
groups [your user name]
```

After you plug in your device, you can check the permissions with:
```
$ ls -l /dev/bus/usb/001/023
crw-rw---- 1 root plugdev 189, 23 Aug 16 00:38 /dev/bus/usb/001/023
```

(Replace /dev/bus/usb/001/023 with your device path; that was mine. It
changes every time you plug in the usb device. You can find it by
seeing which new file appears when you plug in the device.)

That means group plugdev can "rw" the device, and I am in that group, so it works.

You can test which rules are being applied with:
```
udevadm test $(udevadm info -q path -n /dev/bus/usb/001/023)
```

(That's how I finally figured out that my file wasn't being read, because it didn't end in ".rules".)

## Install the service so it runs after reboot:

Have a look at the wensn.service file and adjust the WorkingDirectory, and the path in ExecStart for your setup. If you are not on a Raspberry Pi and running as the default user (pi), you should also adjust the User. Then install the service:

```
sudo cp wensn.service /etc/systemd/system
sudo systemctl enable wensn.service
sudo systemctl start wensn.service
```

You can check that it's "active (running)" with:
```
systemctl status wensn.service
```

The service runs as user pi (not root), so you have to get the device
permissions right (as above). Alternatively, you can change the wensn.service file so it runs as root, but this is generally not a great security practice.

## LogRoll
I also include a python class called LogRoll. This class opens a log file so that you can write SPL values to it. If the filename you provide changes, it rolls over to a new log file. In the filename, I like to include the date and hour, but not the minutes and seconds; this way, when the hour changes, the log file automatically rolls over. The result is a set of timestamped ("hourstamped") log files, each containing all the data for a given hour.

## Credits:

Thanks to ebswift https://www.ebswift.com/reverse-engineering-spl-usb.html for his first crack at reverse engineering this device. This library includes reading the SPL value (bRequest 4), and setting and reading the device modes (bRequests 2 and 3). The device has an SD card for logging, so there may be USB commands to read log files from the SD card. Possibly there is more reverse engineering to be done.
