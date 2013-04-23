#!/usr/bin/python
import find_vm
import scp
import sys
import shutil
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
    execfile("/etc/ssisvmbackup/settings.py", config)

    if len(argv) == 0:
        msg = "Error: please specify VM name"

        sendEmailAlert(msg)
        sys.exit(2)

    vmname = argv[0]

    vmhost = find_vm.findVm(vmname, config["hosts"], config["username"], config["password"])

    if vmhost:
        msg = "VM {0} found in host {1}".format(vmname, vmhost)
        print msg

        # Create working folder in temp folder
        working_folder = os.path.join(config["temp_folder"],"ssisghetto-%s" % vmname)

        remote_folder = os.path.join(config["ghettovcb_remote_folder"],"ssisghetto-%s" % vmname)

        if os.path.isdir(working_folder):
            shutil.rmtree(working_folder)
        os.makedirs(working_folder)
        shutil.copy(os.path.join(config["ghettovcb_local_folder"],config["ghettovcb_script"]),working_folder)

        # Take ghettoVCB template and create a new config file for this VM
        config_file = os.path.join(working_folder,"ghetto-{0}.conf".format(vmname))

        f1 = open(os.path.join(config["ghettovcb_local_folder"],config["ghettovcb_template"]), 'r')
        f2 = open(config_file, 'w')
        for line in f1:
            if line.startswith("EMAIL_SERVER="):
                line = "EMAIL_SERVER=%s\n" % config["smtp_server"]

            if line.startswith("EMAIL_FROM="):
                line = "EMAIL_FROM=%s\n" % config["from_email"]

            if line.startswith("EMAIL_TO="):
                line = "EMAIL_TO=%s\n" % config["admin_email"]

            f2.write(line)

        f1.close()
        f2.close()

        # Copy ghettovcb script and config file to VMWare host
        client = find_vm.connectToHost(vmhost, config["username"], config["password"])
        scpclient=scp.SCPClient(client.get_transport())

        scpclient.put(working_folder, config["ghettovcb_remote_folder"], recursive=True)

        # Execute ghettovcb through Paramiko
        dryrun_flag = ""
        if config["dryrun"]:
            dryrun_flag = " -d dryrun"

        ghetto_command = "{ghettoscript} -m {vmname} -g {configfile} -l {logfile} -w {workingfolder}{dryrun_flag}".format(
            ghettoscript= os.path.join(remote_folder,config["ghettovcb_script"]),
            vmname=vmname,
            configfile= os.path.join(remote_folder,"ghetto-{0}.conf".format(vmname)),
            logfile= os.path.join(remote_folder,"ghetto-{0}.log".format(vmname)),
            workingfolder= os.path.join(remote_folder,"ghetto-{0}.work".format(vmname)),
            dryrun_flag=dryrun_flag
        )

        print "Running: {0}".format(ghetto_command)
        exit_code, output = find_vm.RunCommand(client.get_transport(), ghetto_command)

        # Take the output and mail it to admin
        sendEmailAlert("VMBackup: {vmname} on {vmhost}, result {exit_code}".format(vmname=vmname,vmhost=vmhost,exit_code=exit_code), body=output)

        # Cleanup!
        exit_code, output = find_vm.RunCommand(client.get_transport(), "rm -rf {0}".format(remote_folder))
        shutil.rmtree(working_folder)

        sys.exit(0)
    else:
        print "VM not found!"
        sendEmailAlert("VMBackup: {vmname} NOT FOUND!".format(vmname=vmname))
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])