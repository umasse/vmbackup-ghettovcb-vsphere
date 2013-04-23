#!/usr/bin/python
import paramiko
import scp
import os
import os.path
import sys

# RunCommand is taken from MKSBackup (https://pypi.python.org/pypi/mksbackup)
# This makes this code also GPLv3 or later!

# ---------------------------------------------------------------------------
def RunCommand(t, command, log=None):
    """t is a paramiko transport
    """
    chan=t.open_session()
    exit_code=None
    chan.set_combine_stderr(True)
    cmd_line=command+' ; echo exit_code=$?'
    chan.exec_command(cmd_line)
    output=''
    while 1:
        try:
            x=chan.recv(1024)
            if len(x)==0:
                break
            output+=x
        except socket.timeout:
            break

    exit_code=chan.recv_exit_status()
    chan.close()

    # ESX(i) don't return any usable exit_code, use the one returned by  "echo exit_code=$?"
    pos1=output.rfind('exit_code=')
    pos2=output.find('\n', pos1)
    exit_code=int(output[pos1+10:pos2])
    output=output[:pos1]

    if log:
        l=log.debug
        if exit_code!=0:
            l=log.warning

        if output or exit_code!=0:
            l('exit_code=%d command=%s', exit_code, cmd_line)
            for line in output.split('\n'):
                l('> %s', line)

    return exit_code, output


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

    #srcfile = "ssisghetto"
    #dstfile = "/tmp/"
    #client = connectToHost("172.20.1.21", "root", "xxxxxx")
    #scpclient=scp.SCPClient(client.get_transport())
    #scpclient.put(srcfile, dstfile, recursive=True)

    #main(sys.argv[1:])

    pass
