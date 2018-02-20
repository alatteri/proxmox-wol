#! /bin/sh
"true" '''\'
if command -v python2 > /dev/null; then
  exec python2 "$0" "$@"
else
  exec python "$0" "$@"
fi
exit $?
'''
#    Proxmox Wake On Lan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    dmacias - added fixes for ether proto 0x0842
#    R.A.W. - added LXC containers
import os
import pcap
import sys
import socket
import struct
import string
import logging

files = [fn for fn in os.listdir('/etc/pve/qemu-server') if fn.endswith('.conf')]

class ProxmoxWakeOnLan:
    @staticmethod
    def CheckConfForMac(macaddress):
	confpath = '/etc/pve/qemu-server/'
	for file in os.listdir(confpath):
	    filepath = confpath + file
	    for line in open(filepath):
                if macaddress.upper() in line.upper():
		    return os.path.splitext(os.path.basename(file))[0] + " qm"
	confpath = '/etc/pve/lxc/'
	for file in os.listdir(confpath):
	    filepath = confpath + file
	    for line in open(filepath):
                if macaddress.upper() in line.upper():
			return os.path.splitext(os.path.basename(file))[0] + " pct"
        return False

    @staticmethod
    def StartServerByMACAddress(mac):
        #code to check MAC address
	foundvm = ProxmoxWakeOnLan.CheckConfForMac(mac)
	if foundvm:
	    foundlist = foundvm.split()
	    foundvmid = foundlist[0]
	    command = foundlist[1]
	    checkVM = command + " status " + foundvmid
            status = os.popen(checkVM).read()
            if "running" in status:
		logging.info("Virtual machine already running: %s", foundvmid)
                return False
            else:
		logging.info("Waking up %s", foundvmid)
                startVM = command + " start " + foundvmid
                os.system(startVM)
                return True
		## logging disabled for non-existing MAC, uncomment below line for debugging
       	#logging.info("Didn't find a VM with MAC address %s", mac)
        return False

    @staticmethod
    def GetMACAddress(s):
            # added fix for ether proto 0x0842
            size = len(s)
            bytes = map(lambda x: '%.2x' % x, map(ord, s))
            counted = 0
            macpart = 0
            maccounted = 0
            macaddress = None
            newmac = ""

            for byte in bytes:
                if counted < 6:
                    # find 6 repetitions of 255 and added fix for ether proto 0x0842
                    if byte == "ff" or size < 110:
                        counted += 1
                else:
                    # find 16 repititions of 48 bit mac
                    macpart += 1
                    if newmac != "":
                        newmac += ":"

                    newmac += byte

                    if macpart is 6 and macaddress is None:
                        macaddress = newmac

                    if macpart is 6:
                        #if macaddress != newmac:
                            #return None
                        newmac = ""
                        macpart = 0
                        maccounted += 1

            if counted > 5 and maccounted > 5:
                return macaddress

    @staticmethod
    def DecodeIPPacket(s):
        if len(s) < 20:
            return None
        d = {}
        d['version'] = (ord(s[0]) & 0xf0) >> 4
        d['header_len'] = ord(s[0]) & 0x0f
        d['tos'] = ord(s[1])
        d['total_len'] = socket.ntohs(struct.unpack('H', s[2:4])[0])
        d['id'] = socket.ntohs(struct.unpack('H', s[4:6])[0])
        d['flags'] = (ord(s[6]) & 0xe0) >> 5
        d['fragment_offset'] = socket.ntohs(struct.unpack('H', s[6:8])[0] & 0x1f)
        d['ttl'] = ord(s[8])
        d['protocol'] = ord(s[9])
        d['checksum'] = socket.ntohs(struct.unpack('H', s[10:12])[0])
        d['source_address'] = pcap.ntoa(struct.unpack('i', s[12:16])[0])
        d['destination_address'] = pcap.ntoa(struct.unpack('i', s[16:20])[0])
        if d['header_len'] > 5:
            d['options'] = s[20:4 * (d['header_len'] - 5)]
        else:
            d['options'] = None
        d['data'] = s[4 * d['header_len']:]
        return d

    @staticmethod
    def InspectIPPacket(pktlen, data, timestamp):
        if not data:
            return
        decoded = ProxmoxWakeOnLan.DecodeIPPacket(data[14:])
        macaddress = ProxmoxWakeOnLan.GetMACAddress(decoded['data'])
        if not macaddress:
            return
	return ProxmoxWakeOnLan.StartServerByMACAddress(macaddress)

if __name__ == '__main__':
    from pmwolutils import Utils
    Utils.SetupLogging()

    # line below is replaced on commit
    LVWOLVersion = "20140814 231218"
    Utils.ShowVersion(LVWOLVersion)

    if len(sys.argv) < 2:
        print('usage: proxmoxwol <interface>')
        sys.exit(0)

    interface = sys.argv[1]
    p = pcap.pcapObject()
    net, mask = pcap.lookupnet(interface)
    # set promiscuous to 1 so all packets are captured
    p.open_live(interface, 1600, 1, 100)
    # added support for ether proto 0x0842
    p.setfilter('udp port 7 or udp port 9 or ether proto 0x0842', 0, 0)


    while True:
        try:
            p.dispatch(1, ProxmoxWakeOnLan.InspectIPPacket)
        except KeyboardInterrupt:
            break
        except Exception:
            continue
