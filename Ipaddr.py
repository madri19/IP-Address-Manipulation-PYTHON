import socket
import fcntl
import struct
import re
import subprocess
import time
from subprocess import check_output
import os
from netaddr import IPNetwork, IPAddress


# Get the Ip Address
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


# Extract the IP Address and break it up into parts from the periods
def extractip(ipstr):
    l = re.split("(.*)\.(.*)\.(.*)\.(.*)", ipstr)
    return l[1:-1]


def set_new_ip(ip):
    subprocess.call(["sudo", "ifconfig", "eth0", ip, "netmask", "255.255.255.0"])
    time.sleep(1)
    return get_ip_address('eth0')


def setHostName(node):
    newName = "formation-table-" + str(node)

    # check if the hostname we want is in the /etc/hosts file
    out2 = 'sudo grep -q ' + newName + ' /etc/hosts && echo "yes" || echo "no"'
    out4 = os.popen(out2).read()

    if not out4 == "yes\n":
        out3 = 'sudo sed -i "/\w\m\w/d" /etc/hosts && sudo vim -c "2 s/^/127.0.0.1\t' + newName + \
               '\r/" -c "wq!" /etc/hosts'
        os.system(out3)

    # check if we already have the host name set for hostname command
    out = check_output(["hostname"])

    # if we dont have the hostname we want then set it
    if not out == newName + '\n':
        subprocess.call(["sudo", "hostnamectl", "set-hostname", newName])

    return newName


def ip_setup(node):

    # First build what we expect!
    oct_valueTrue = extractip(get_ip_address('eth0'))
    oct_valueDummy = [oct_valueTrue[0], oct_valueTrue[1], oct_valueTrue[2], "000"]
    # change to the value from the node if dip  == 1 then we want 101
    if node <= 9:
        oct_valueDummy[3] = '10' + str(node)
    else:
        oct_valueDummy[3] = '1' + str(node)

    if oct_valueTrue != oct_valueDummy:
        # Rebuild the IP Address
        new_ip = str(oct_valueTrue[0]) + '.' + str(oct_valueTrue[1]) + '.' + str(oct_valueTrue[2]) + '.' \
                 + str(oct_valueDummy[3])
        # build our network range to change
        check_network = str(oct_valueTrue[0]) + '.' + str(oct_valueTrue[1]) + '.' + str(oct_valueTrue[2]) + '.' + '0/24'
        # Check if this ip address is already taken
        text_file8 = open("/home/messages-log.txt", "a")
        #if IPAddress(new_ip) in IPNetwork(check_network):
        #    print(new_ip + " <-- This IP Address/Node is already taken by another Pi/Device.\n" +
        #          "Please make sure your node selection is correct on the Pi Hat PCB and reset it.\n" +
        #          "If this errors continues please check the node selection of the rest of the pis for correct node #.")
        #    text_file8.write(new_ip + " <-- This IP Address/Node is already taken by another Pi/Device.\n" +
        #                     "Please make sure your node selection is correct on the Pi Hat PCB and reset it.\n" +
        #                     "If this errors continues please check the node selection of the rest of the pis for " +
        #                     "correct node #.\n")
        #    text_file8.close()
        #    while 1:
        #        time.sleep(3)
        #else:
            # Now set the new ip
        while new_ip != set_new_ip(new_ip):
            time.sleep(1)
        #    print("New IP Address has been set!")
        #    text_file8.write("New IP Address has been set!\n")
        #    text_file8.close()

    # Grab the Original or changed IP Address
    data1 = "IP:\t\t" + get_ip_address('eth0')

    text_file5 = open("/home/messages-log.txt", "a")
    print(data1)
    text_file5.write(data1 + "\n")
    # Set the new hostname
    data2 = "Host Name: " + setHostName(node)
    print(data2)
    text_file5.write(data2 + "\n")
    text_file5.close()
