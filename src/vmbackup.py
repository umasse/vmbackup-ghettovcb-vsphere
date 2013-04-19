#!/usr/bin/python
import find_vm
import sys
import os
import os.path
import subprocess

# Imports for sending email alerts
import smtplib
from email.mime.text import MIMEText

config = {}

def sendEmailAlert(title, body=None):
    if not body:
        body = title

    msg = MIMEText(body)

    msg['Subject'] = title
    msg['From'] = config["from_email"]
    msg['To'] = config["admin_email"]

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(config["smtp_server"])
    s.sendmail(msg['From'], [ msg['To'] ], msg.as_string())
    s.quit()


def main(argv):
    execfile("settings.py", config)

    if len(argv) == 0:
        msg = "Error: please specify VM name"

        sendEmailAlert(msg)
        sys.exit(2)

    vmname = argv[0]

    vmhost = find_vm.findVm(vmname, config["hosts"], config["username"], config["password"])

    if vmhost:
        msg = "VM found in host %s" % vmhost

        # Take mksbackup template and create a new config file for this VM
        config_file = os.path.join(config["mksbackup_config_dir"],"%s.ini" % vmname)

        f1 = open(os.path.join(config["mksbackup_config_dir"],config["mksbackup_template"]), 'r')
        f2 = open(config_file, 'w')
        for line in f1:
            if line.startswith("host="):
                line = "host=%s\n" % vmhost
            if line.startswith("vm_list="):
                line = "vm_list=%s\n" % vmname

            if line.startswith("smtp_host="):
                line = "smtp_host=%s\n" % config["smtp_server"]

            if line.startswith("sender="):
                line = "sender=%s\n" % config["from_email"]

            if line.startswith("recipients="):
                line = "recipients=%s\n" % config["admin_email"]

            if line.startswith("login="):
                line = "login=%s\n" % config["username"]

            if line.startswith("password="):
                line = "password=%s\n" % config["password"]

            f2.write(line)

        f1.close()
        f2.close()

        # Execute mksbackup
        mksbackup_cmd = ['/usr/local/bin/mksbackup', '-c', config_file, '-l', config["mksbackup_log"], '-q', 'backup', 'SSIS_BACKUP' ]

        print "Backing up using this command:"
        print subprocess.list2cmdline(mksbackup_cmd)

        p = subprocess.Popen(mksbackup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        sys.exit(0)
    else:
        print "VM not found!"
        sys.exit(1)

if __name__ == "__main__":
   main(sys.argv[1:])