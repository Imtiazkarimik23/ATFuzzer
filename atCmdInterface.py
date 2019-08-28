#!/usr/bin/env python2

import sys
import os
import signal
import time
import random
import utilityFunctions
import logging
import serial
import socket
#import bluetooth
import subprocess
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
from stat import S_ISCHR

size = 99999

# --- Bluetooth MAC address of the target device --- #
#serverMACAddress = '18:E2:C2:5E:29:1C' #S3
#serverMACAddress = '50:55:27:5f:16:7d' #Nexus5
#serverMACAddress = '94:8B:C1:43:0E:C4' #S8plus
#serverMACAddress = '40:4E:36:AF:01:94' #htc
#serverMACAddress = 'e4:90:7e:ee:2b:84' #nexus6
#serverMACAddress = '04:B1:67:57:58:B9' #xiaomi
serverMACAddress = '14:A5:1A:48:0A:2D' #huwaei


try:
    import readline
except ImportError:
    import pyreadline as readline

# Global vars
environment = ''

DEFAULT_BAUD = 115200
DEFAULT_TIMEOUT = 1

log_file = "log/atsend.log"

log_level = logging.DEBUG
baud_rate = 115200
time_out = 1
mfuzz_port = None
max_poll = 4
poll_delay = 2
format_string = ["<value>", "%d", "%u", "%s", "%c", "%x", "<n>", "<index>", "<args>", "<gain>"]
debug_cmd_gen = True


# Description:
def create_serial(port, baud):
    # print("Creating serial port %s @ %d baud" % (port, baud))
    return serial.Serial(port, baud, timeout=DEFAULT_TIMEOUT)


# Description:
def recv():
    my_poll = 0
    lines = []

    # Make sure we dont go _too_ fast
    start_time = time.time()

    # To deal with the response delay
    while my_poll < max_poll:
        line = mfuzz_port.readline()
        # print line
        # timeout
        if line == "":
            my_poll += 1
            # time.sleep(poll_delay)
            continue

        # clean up the output for comparison
        line_clean = line.strip('\r\n')

        lines += [line]
        # print line_clean

        # a terminal response. end NOW
        if 'ERROR' == line_clean:
            break
        elif 'CME ERROR' in line_clean:
            break
        elif 'OK' == line_clean:
            break
        elif 'NO CARRIER' == line_clean:
            break
        elif 'ABORTED' == line_clean:
            break
        elif 'NOT SUPPORTED' == line_clean:
            break
        else:
            continue

    # "Do you know how fast you were going?"
    # if time.time() - start_time < 1.0:
    # time.sleep(2)

    # post-processing
    lines2 = []
    for l in lines:
        if l == '\r\n':
            continue
        if l.endswith('\r\n'):
            lines2.append(l[:-1])
    return lines2


# Description:
def send(cmd):
    '''
	True - sending failed
	False - sending successful
	'''
    cmd2 = str(cmd)
    mfuzz_port.write(cmd2 + '\r\r')


# Description: 
def bluetooth_send(cmd):
	'''
	True - sending failed
	False - sending successful
	'''
	data = "NULL"
	backlog = 1
	cmd2 = str(cmd)
	try:
		s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		s.connect((serverMACAddress, port))
		#s.bind((serverMACAddress, port))
		#s.listen(backlog)
	except Exception as e:
		print "error occured"
		print e
		s.close()
		subprocess.call("sudo /etc/init.d/bluetooth restart",shell=True)
		time.sleep(15)
		#send_blue(cmd)
	try:
		s.send(cmd +"\r\r")
		data=s.recv(size)
		print data
		time.sleep(5)
		s.close()
		return data
		#return
	except:
		subprocess.call("sudo /etc/init.d/bluetooth restart",shell=True)
		time.sleep(15)
		#send_blue(cmd)


# Description:
def extend(cmds):
    '''
	Extend the cmd list
	'''
    cmds2 = []
    for c in cmds:
        cmds2.append(c)
        if c.endswith("="):
            cmds2.append(c[:-1])
    return cmds2


# Description:
def check_internet_connectivity(output):
	flag = 0
	if "mDataConnectionState=0" in output:
		return 1
	#if "UMTS" in output:
		#return 1
	#if "GSM EDGE" in output:
		#return 1
	return flag


# Description:
def at_probe():
    found = []
    if environment == 'linux':
        print('Probing for ttyACM devices...')
        for i in range(10):
            devname = '/dev/ttyACM%d' % i
            if not os.path.exists(devname):
                continue
            mode = os.stat(devname).st_mode
            if S_ISCHR(mode):
                found += [devname]

    elif environment == 'windows':
        print('Probing for COM ports...')
        for i in range(256):
            port = 'COM%d' % i
            try:
                s = serial.Serial(port)
                s.close()
                found.append(port)
            except (OSError, serial.SerialException):
                pass
    else:
        raise Exception('EnvironmentError: unknow OS')
    return found


# Description:
def send_at_command(ser, cmd):
    start = time.time()
    ser.write(cmd + "\r")
    lines = []

    while True:
        line = ser.readline()

        # timeout
        if line == "":
            break

        # clean up the output (we dont want line endings)
        line_clean = line.strip('\r\n')

        lines += [line_clean]

        if 'ERROR' == line_clean:
            break
        elif 'CME ERROR' in line_clean:
            break
        elif 'OK' == line_clean:
            break
        elif 'NO CARRIER' == line_clean:
            break
        elif 'ABORTED' == line_clean:
            break
    end = time.time()
    print end - start
    return lines


# Description:
def at_connect(dev, baud=DEFAULT_BAUD):
    try:
        ser = create_serial(dev, baud)
    except:
        ser = None

    if ser != None:
        resp = send_at_command(ser, 'AT')
        if len(resp) > 0 and resp[-1] == 'OK':
            return ser
        ser.close()
    return None


# Description:
def check_sim_connectivity(output):
    output = output[:150]
    # print output
    return 1 if "mServiceState=1 1" in output else 0


# Description:
def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


# Description:
def set_environment():
    global environment
    if os.name == 'posix':
        environment = 'linux'
    elif os.name == 'nt':
        environment = 'windows'
    else:
        raise Exception('EnvironmentError: unknow OS')


# Description:
def get_serial_connection(dev):
    set_environment()
    devices = at_probe() if (dev == None) else [dev]

    if len(devices) == 0:
        print "No devices found"
        return
    for d in devices:
        print 'Trying device ', d
        ser = at_connect(d)
        if ser is not None:
            return ser
    return None


# Description:
from subprocess import check_output
def get_pid(name):
    return int(check_output(["pidof", name]))


# Description:
def test_adb_process():
    attempt = 5
    test = False
    delay = 1
    while not test:
        if attempt == 0:
            raise Exception('Error: cannot execute adb command - adb process is not responding')
        timeout = 31
        task = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while task.poll() is None and timeout > 0:
            time.sleep(delay)
            timeout -= delay
        if timeout > 0:
            test = True
        else:
            os.kill(get_pid('adb'), signal.SIGTERM)
            attempt -= 1


# Description: 
# reboot adb and the connected device
def reboot_env(device=None):
    # test_adb_process()
    subprocess.call("adb kill-server", shell=True)
    subprocess.call("adb reboot", shell=True)
    subprocess.call("adb kill-server", shell=True)

    if environment == 'linux':
        subprocess.call(['./test.sh'], shell=True)
    elif environment == 'windows':
        subprocess.call(['test.bat'], shell=True)
    else:
        raise Exception('EnvironmentError: unknow OS')
    subprocess.call("adb kill-server", shell=True)
    cmd = ['adb', 'shell', 'su']
    procId = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    if device == 'htcDesire10':
        procId.communicate('setprop sys.usb.config mtp,adb,diag,modem,modem_mdm,diag_mdm\nexit\n')
    elif device == 'huaweiNexus6P' or device is None:
        pass
    else:
        procId.communicate('setprop sys.usb.config diag,adb\nexit\n')

    time.sleep(8)


# Description: 
def init_mfuzz_port(device, port):
    global mfuzz_port
    mfuzz_port = get_serial_connection(port)
    if mfuzz_port is None:
        if device == 'samsungNote2' or device == 'samsungGalaxyS3':
            try:
                init_mfuzz_port(device, port)
                return
            except:
                pass
        reboot_env(device)
        init_mfuzz_port(device, port)


# Description: 
def write_on_logcat(stime, ftime):
    command = 'adb logcat -v time -d *:E'.split()
    logcat = ''
    for line in run_command(command):
        splitted = line.split()
        timevalue = splitted[0] + ' ' + splitted[1]
        timevalue = '2019-' + timevalue
        try:
            datetime_object = datetime.strptime(timevalue, '%Y-%m-%d %H:%M:%S.%f')
            # datetime_object = timedelta(year=2019)
            # print datetime_object

            if stime <= datetime_object <= ftime:
                if (line not in logcat) and ("/QC-time-services" not in line) and ("WakeLock( 2253)" not in line) and (
                        "EarsSyncAdapter(10719)" not in line) and \
                        ("ACDB AudProc vol returned = -19" not in line):
                    logcat += line
        except:
            pass

    f = open("logcat.txt", "a")
    f.write(logcat)
    f.close()


# Description: 
def bluetooth_fuzz(cmd):
	retList = []
	flag = 0
	timer_for_check = 50
	cmd = str("AT"+cmd)
	print cmd
	start = time.time()
	stime = datetime.now()
	print stime
	try:
		r = bluetooth_send(cmd)
	except serial.serialutil.SerialException as e:
		print e	
	end = time.time()
	total_time = (end-start)/len(cmd)	# normalize the total time based on the command length
	ftime = datetime.now() + timedelta(minutes=1)
	retList.append(total_time)
	print "Input: "+cmd+" Output: "+str(r)
	if r is None:
		retList.append(flag)
		return retList

	r = str(r).rstrip("\r\n")
	if "ERROR" not in r:
		print r + "in"
		flag = 1
		retList.append(flag)
		#time.sleep(15)
		return retList

	for _ in range(timer_for_check):
		command = 'adb shell dumpsys telephony.registry'.split()
		output = ""
		for line in run_command(command):
			output+=line

		flag1 = check_sim_connectivity(output)
		flag2 = check_internet_connectivity(output)
		time.sleep(0.5)
		if flag1==1 or flag2==1:
			print "in here"
			flag =1
			print "flag is now " +str(flag)
			time.sleep(5)
			break
		else:
			print "flag is now yo" +str(flag)

	retList.append(flag)
	print retList
	return retList


# Description: 
def usb_fuzz(cmd, device, port=None):
    retList = []
    flag = 0
    # time.sleep(5)
    # Open the serial port
    init_mfuzz_port(device, port)
    print 'Serial port: ', mfuzz_port.port
    logging.info("port is opened for %s" % mfuzz_port.port)

    # Fuzz
    timer_for_check = 20
    print cmd
    cmd = str(cmd)
    start = time.time()
    stime = datetime.now()
    print stime
    try:
        send(cmd)
    except serial.serialutil.SerialException as e:
        if device == 'samsungNote2' or device == 'samsungGalaxyS3' or device == "LGg3":
            try:
                return usb_fuzz(cmd, device, port)
            except:
                pass
        print e
        mfuzz_port.close()
        reboot_env(device)
        return usb_fuzz(cmd, device, port)

    r = recv()
    end = time.time()
    total_time = (end - start) / len(cmd)  # normalize the total time based on the command length
    ftime = datetime.now() + timedelta(minutes=1)
    retList.append(total_time)
    print r
    if "OK\r" in r:  # cut phone Go to sleep got phone call
        # time.sleep(1)
        #send("AT+CHUP")
        r10 = recv()
        #time.sleep(2)
        #cmd2 = cmd + '\r\r'
        #flag = 0 if (len(r) == 2 and cmd2 in r) or (len(r) == 1) else 1
        flag  = 1
        retList.append(flag)
        return  retList

    for _ in range(timer_for_check):
        # test_adb_process()
        # if device == 'nexus5':
        #	write_on_logcat(stime, ftime)

        command = 'adb shell dumpsys telephony.registry'.split()
        output = ""
        for line in run_command(command):
            output += line

        flag1 = check_sim_connectivity(output)
        flag2 = check_internet_connectivity(output)
        time.sleep(0.5)
        if flag1 == 1 or flag2 == 1:
            flag = 1
            print "flag is now " + str(flag)
            time.sleep(5)
            break
        else:
            print "flag is now " + str(flag)
    retList.append(flag)
    print retList
    mfuzz_port.close()
    logging.info("port is closed")
    return retList


# Description:
def test_fuzz(cmd):
    return [random.random()*5, utilityFunctions.flip_coin(10)]


def main():
    usb_fuzz("ATD123", 'test_dev')
    # logging.info("atsend/mfuzz ends...")
    print '\n--- Test Completed ---\n'


if __name__ == "__main__":
    main()
