# proxmox-wol

Usage:
- Unzip contents of attachment to a directory of your choosing, e.g. /root/scripts
- Create folder /var/log/proxmoxwol - a file named proxmoxwol.log will be created and all logs sent here. Additionally, the below init script will log into this directory.
- To start the service at boot, copy (and rename) the proxmoxwol.init file from the zip contents to '/etc/init.d/proxmoxwol', set as executable with 'chmod +x proxmoxwol' - and then enable with 'update-rc.d proxmoxwol defaults'.
- Make sure to modify the cmd and int variables as required in /etc/init.d/proxmoxwol for your script location and bridged network adapter.
- To rotate the logs, which can get quite large if there are frequent WOL requests, copy (and rename) proxmoxwol.logrotate to file '/etc/logrotate.d/proxmoxwol'.
- Install pcap with `apt-get install python-libpcap`
- Either reboot or issue '/etc/init.d/proxmoxwol start' and check the above mentioned log file for status and/or errors.
