# SSISVMBackup
====================
Python helper scripts, using Paramiko, scp.py and ghettoVCB to conveniently backup guests from multiple VMWare hosts.

Assuming vMotion is on, it first checks each host until it finds where the VM is currently running. Quickly prepares a customized ghettoVCB.conf file, and uses scp.py to upload it, and ghettoVCB.sh, to the correct host. Finally starts ghettoVCB using Paramiko, capturing output and emailing it back to the ICT administrator.

Currently I'm using it to backup to persistent NFS, using Ubuntu server with ZFS-on-Linux with compression and deduplication turned on.
SSIS stands for Saigon South International School :)


## References:
==============
Paramiko: http://www.lag.net/paramiko/

scp.py: https://github.com/jbardin/scp.py

ghettoVCB: https://github.com/lamw/ghettoVCB

## Example
==========

    $ /usr/local/lib/ssisvmbackup/vmbackup.py Server-Minecraft
    VM Server-Minecraft found in host 10.2.2.24
    Running: /tmp/ssisghetto-Server-Minecraft/ghettoVCB.sh -m Server-Minecraft -g /tmp/ssisghetto-Server-Minecraft/ghetto-Server-Minecraft.conf -l /tmp/ssisghetto-Server-Minecraft/ghetto-Server-Minecraft.log -w /tmp/ssisghetto-Server-Minecraft/ghetto-Server-Minecraft.work
