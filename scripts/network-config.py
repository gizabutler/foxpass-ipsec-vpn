#!/usr/bin/python
from urllib2 import urlopen, Request
import ifaddr
import subprocess
from jinja2 import FileSystemLoader, Environment
from os import chown, chmod, geteuid, urandom


METADATA_BASE_URL = "http://169.254.169.254/"
private_ip = ['172.16.1.100', '172.16.0.100']


def get_address(private_ip):
    adapters = urlopen(METADATA_BASE_URL +
                       'latest/meta-data/network/interfaces/macs/').read()
    for adapter in adapters.split():
        ip = urlopen(METADATA_BASE_URL + 'latest/meta-data/network/interfaces/macs/' +
                     adapter + '/local-ipv4s/').read()
        if ip in private_ip:
            return ip
# TODO: while loop to wait for ENI


address = get_address(private_ip)


def get_gateway(address):
    if address == '172.16.0.100':
        gateway = '172.16.0.1'
        return gateway
    elif address == '172.16.1.100':
        gateway = '172.16.1.1'
        return gateway


gateway = get_gateway(address)


def write_to_cfg(address):
    # * write IP `to eth1.cfg
    file_loader = FileSystemLoader("/opt/templates/")
    env = Environment(loader=file_loader)
    template = env.get_template('eth1.cfg')
    output = template.render(PRIVATE_IP=address, GATEWAY=gateway)
    fname = "/etc/network/interfaces.d/eth1.cfg"
    with open(fname, 'w') as f:
        f.write(output)
    return output
    # * set /etc/network/interfaces.d/eth1.cfg to be owned and only accessible by root
    chmod('/etc/network/interfaces.d/eth1.cfg', 0600)
    chown('/etc/network/interfaces.d/eth1.cfg', 0, 0)
# TODO: write gateway to templated file

output = write_to_cfg(address)

# ! not working
def restart_services():
    subprocess.call(['systemctl', 'restart', 'networking'], shell=False)
    subprocess.call(['systemctl', 'start', 'pacemaker'], shell=False)
    subprocess.call(['systemctl', 'start', 'corosync'], shell=False)


def main():
    get_address
    get_gateway
    write_to_cfg
    restart_services


if __name__ == '__main__':
    main()
