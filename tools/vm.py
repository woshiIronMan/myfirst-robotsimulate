#!/usr/bin/env python
"""Minimal SSH helper for the C26 Ubuntu VM (paramiko).

Usage:
    python tools/vm.py "command"            # run command, print stdout+stderr
    python tools/vm.py -f script.sh         # run a local script on the VM
    python tools/vm.py --put local remote   # copy a file to the VM
    python tools/vm.py --get remote local   # copy a file from the VM
"""
import sys
import os
from functools import cache
from getpass import getpass

import paramiko

HOST = os.environ.get("C26_VM_HOST", "192.168.100.128")
USER = os.environ.get("C26_VM_USER", "xue")
PORT = int(os.environ.get("C26_VM_PORT", "22"))


@cache
def vm_password():
    return os.environ.get("C26_VM_PASS") or getpass(f"{USER}@{HOST} password: ")


def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=vm_password(),
              look_for_keys=False, allow_agent=False, timeout=20)
    return c


def run(cmd, timeout=600, get_pty=False):
    c = connect()
    try:
        stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout, get_pty=get_pty)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err
    finally:
        c.close()


def main():
    args = sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args:
        print(__doc__)
        return 1

    if args[0] == "--put":
        c = connect()
        sftp = c.open_sftp()
        sftp.put(args[1], args[2])
        sftp.close()
        c.close()
        print("put ok:", args[1], "->", args[2])
        return 0

    if args[0] == "--get":
        c = connect()
        sftp = c.open_sftp()
        sftp.get(args[1], args[2])
        sftp.close()
        c.close()
        print("get ok:", args[1], "->", args[2])
        return 0

    if args[0] == "-f":
        with open(args[1], "rb") as f:
            payload = f.read()
        c = connect()
        sftp = c.open_sftp()
        remote = "/tmp/_vm_script_%d.sh" % os.getpid()
        with sftp.open(remote, "wb") as rf:
            rf.write(payload)
        sftp.chmod(remote, 0o755)
        sftp.close()
        # sudo -S with password from stdin
        cmd = "sudo -S -p '' bash %s" % remote
        stdin, stdout, stderr = c.exec_command(cmd, timeout=3600)
        stdin.write(vm_password() + "\n")
        stdin.flush()
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        rc = stdout.channel.recv_exit_status()
        c.close()
        print(out, end="")
        if err.strip():
            print("--- stderr ---", file=sys.stderr)
            print(err, end="", file=sys.stderr)
        return rc

    cmd = " ".join(args)
    rc, out, err = run(cmd)
    print(out, end="")
    if err.strip():
        print("--- stderr ---", file=sys.stderr)
        print(err, end="", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
