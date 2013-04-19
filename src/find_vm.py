#!/usr/bin/python
import paramiko
import os
import os.path
import sys

def connectToHost(vmhost, username, password, port=22):
    # Connect to host
    #print "connectToHost (%s, %s, %s)" % (vmhost, username, password)

    client = None
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)

        client.connect(vmhost, port=port, username=username, password=password)

        return client
    except:
        return None

    return client

def getVmList(vmhost, username, password):
    vmlist = []

    client = connectToHost(vmhost, username, password)

    command = "vim-cmd vmsvc/getallvms | grep vmx"

    if client:
        stdin, stdout, stderr = client.exec_command(command)

        for line in stdout.readlines():
            # We need token 1 to one less than token starting with "["
            linetokens = line.split()
            for token in linetokens:
                if token.startswith("["):
                    # This token is the start of the datastore location
                    vmname = ' '.join(linetokens[1:linetokens.index(token)])
                    vmlist.append(vmname)

    return vmlist


def isVmInHost(vmname, vmhost, username, password):
    #print "isVmInHost (%s, %s, %s, %s)" % (vmname, vmhost, username, password)

    vmlist = getVmList(vmhost, username, password)

    if vmlist:
        return vmname in vmlist

    return False


def findVm(vmname, vmhosts, username, password):
    for vmhost in vmhosts:
        #print "Checking host %s" % vmhost
        vmfound = isVmInHost(vmname, vmhost, username, password)
        if vmfound:
            return vmhost

    return None


def main(argv):
    config = {}
    execfile("settings.py", config)

    #print config["hosts"]
    if "hosts" not in config.keys() or len(config["hosts"]) < 0:
        print "Error: Missing hosts setting"
        sys.exit(2)

    if "username" not in config.keys() or len(config["username"]) < 0:
        print "Error: Missing username setting"
        sys.exit(2)

    if "password" not in config or len(config["password"]) < 0:
        print "Error: Missing password setting"
        sys.exit(2)

    if len(argv) == 0:
        print "Error: please specify VM name"
        sys.exit(2)

    vmname = argv[0]
    print "Searching for VM \"%s\"" % vmname

    vmhost = findVm(vmname, config["hosts"], config["username"], config["password"])

    if vmhost:
        print "VM found in host %s" % vmhost
        sys.exit(0)
    else:
        print "VM not found!"
        sys.exit(1)

if __name__ == "__main__":
   main(sys.argv[1:])