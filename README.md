# proxmox-wol

Usage:
- Unzip the master.zip to your home dir
- Everything below this needs to be done as root
- Install pcap with `apt install python-libpcap`
- Create folder: mkdir /etc/pve-wol
- copy or move unzipped files to the directory /etc/pve-wol (just the files)
- Create folder: mkdir /var/log/proxmoxwol - a file named proxmoxwol.log will be created and all logs sent here. Additionally, the init script will log into this directory.
- To start the service at boot, copy (and rename) the proxmoxwol.init file from the zip contents to '/etc/init.d/proxmoxwol', set as executable with 'chmod +x proxmoxwol' - and then enable with 'update-rc.d proxmoxwol defaults'.
- Make sure to modify the cmd and int variables as required in /etc/init.d/proxmoxwol for your script location and bridged network adapter.
- To rotate the logs, which can get quite large if there are frequent WOL requests, copy (and rename) proxmoxwol.logrotate to file '/etc/logrotate.d/proxmoxwol'.
- Either reboot or issue '/etc/init.d/proxmoxwol start' and check the above mentioned log file for status and/or errors.
