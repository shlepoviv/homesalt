"""
module for audit minion
"""

import platform
import re
import subprocess
import logging
import os
import json
import ipaddress
import hashlib

import salt.utils.cache as cache

log = logging.getLogger(__name__)


def _linux_cdm(cmd:list[str],timeout:int = 3):
    with subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT) as proc:

        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subprocess.SubprocessError as e:
            proc.kill()
            log.debug(f'audit _linux_cdm: {e}')
            return 'None'
    return outs.decode('utf-8').rstrip()

def _linux_add_kernel(invent:dict):

    invent["host_os_release"] = _linux_cdm(['uname','-r'])
    invent["host_os_kernel"] = _linux_cdm(['uname','-v'])
    invent["host_os_kernel_full"] = _linux_cdm(['uname','-a'])

def _linux_add_version(invent:dict):  

    host_os_par = {"NAME": "host_os_name",
                   "VERSION_ID": "host_os_version"
                   }
    file_version = '/etc/os-release'
    if os.path.exists(file_version):
        with open(file_version, "r",encoding='utf-8') as f:
            regex = re.compile("^([\w]+)=(?:'|\")?(.*?)(?:'|\")?(\\n)?$")
            for line in f:
                match = regex.match(line.strip())
                if match:
                    if match.group(1) in host_os_par:
                        invent[host_os_par[match.group(1)]] = re.sub(
                            r'\\([$"\'\\`])', r"\1", match.group(2)
                        )
    else:
        log.debug(f'audit: file {file_version} is not exist')                       

def _linux_add_bios(invent:dict):
    host_os_par = {
        "host_bios_version": "bios_version",
        "biosreleasedate": "bios_date",
        "host_serial_number": "product_serial",
        'host_model':'board_name',
        'host_vendor':'board_vendor'
    }
    for key, fw_file in host_os_par.items():
        contents_file = os.path.join("/sys/class/dmi/id", fw_file)
        if os.path.exists(contents_file):
            with open(contents_file, "r") as ifile:
                invent[key] = ifile.read().strip()
        else: 
            log.debug(f'audit: file /sys/class/dmi/id/{fw_file} is not exist')

def _linux_cpudata(invent:dict):
    file_cpuinfo = '/proc/cpuinfo'
    if os.path.exists(file_cpuinfo):
        invent["host_cpu_core"] = 0
        physical_id = set()
        with open(file_cpuinfo,'r',encoding='utf-8') as f:
            for line in f:
                par = line.strip().split(':')
                
                if len(par) == 2:
                    key = par[0].strip()
                    val = par[1].strip()
                    if key == 'processor':
                        invent['host_cpu_core'] += 1
                    elif key  == 'physical id':
                        physical_id.add(val)
                    elif key  == 'model name':
                        invent["host_cpu_type"] = val 

        invent["host_cpu_socket"] = len(physical_id)
    else: 
        log.debug(f'audit: file /sys/class/dmi/id/{file_cpuinfo} is not exist')

def _linux_memdata(invent:dict):
    file_meminfo = '/proc/meminfo'
    host_mem_par = {
        'MemTotal':'host_ram',    
        'SwapTotal':'swap_memory_size'
    }
    if os.path.exists(file_meminfo):
        with open(file_meminfo,'r',encoding='utf-8') as f:
            for line in f:
                par = line.strip().split(':')
                
                if len(par) == 2:
                    key = par[0].strip()
                    val = par[1].strip()
                    if key in host_mem_par:
                        invent[host_mem_par[key]] = int(val.split()[0]) // 1024
    else: 
        log.debug(f'audit: file /sys/class/dmi/id/{file_meminfo} is not exist') 

def _linux_host_disk2stor_map(invent:dict):
    def convert_size(disk:dict):
        if 'size' in disk:
            disk['size'] = int(disk['size']) // 1024 // 1024
        if 'children' in disk:
            for c in disk['children']:
                convert_size(c)

    colums = 'NAME,SERIAL,VENDOR,MODEL,SIZE,TYPE,MOUNTPOINT,PKNAME,KNAME'
    out = _linux_cdm(['lsblk','-J','-b','-o',colums])
    try:
        invent["host_disk2stor_map"] = json.loads(out)['blockdevices']
        for disk in invent["host_disk2stor_map"]:
            convert_size(disk)        
    except json.JSONDecodeError:
        log.debug('audit: _linux_host_disk2stor_map JSONDecodeError, input{out}')
        invent["host_disk2stor_map"] = []


    
def _linux_hostnames(invent:dict):
    invent['host_dns_name'] = _linux_cdm(['hostname','-f'])
    invent['hostname'] = _linux_cdm(['hostname','-s'])

    

def _linux_netatapter(invent:dict):
    out = _linux_cdm(['ip','-j','-d','a'])
    list_adapt = []
    for a in adaptdata:
        adapt = {}
        adapt['name'] = a['ifname']
        adapt['mac_address'] = a['address']
        adapt['ips_info'] = []
        for addr in a['addr_info']:
            i = ipaddress.ip_interface(f'{addr["local"]}/{addr["prefixlen"]}')
            adapt['ips_info'].append({"ip": str(i.ip),
                                     "netmask": str(i.netmask),
                                     "network": str(i.network),
                                     "alias": addr.get('label','')})
        list_adapt.append(adapt)
    invent['host_netadapter_html'] = list_adapt

def _linux_ip_address(invent:dict):
    invent['host_ip_address'] = _linux_cdm(['hostname','-i'])
    out = _linux_cdm(['hostname','-I']).split()
    out.append(invent['host_ip_address'])
    invent['host_ip_addresses'] = out

def _linux_add_dns_servers(invent:dict):
    file_meminfo = '/run/systemd/resolve/resolv.conf'
    invent['host_dns_server']=[]
    if os.path.exists(file_meminfo):
        with open(file_meminfo,'r',encoding='utf-8') as f: 
            for line in f:
                if line.startswith('nameserver'):
                    invent['host_dns_server'].append(line.split()[1])
    else: 
        log.debug(f'audit: file {file_meminfo} is not exist') 

def _linux_add_users(invent:dict):
    file_meminfo = '/etc/passwd'
    invent['host_users']=[]
    if os.path.exists(file_meminfo):
        with open(file_meminfo,'r',encoding='utf-8') as f: 
            for line in f:
                u = line.strip().split(':')
                invent['host_users'].append({
                    "username": u[0],
                    "uid": int(u[2]),
                    "gid": int(u[3]),
                    "home_dir": u[5],
                    "shell": u[6]

                })
    else: 
        log.debug(f'audit: file {file_meminfo} is not exist') 

def _linux_add_pkgs_list(invent:dict):
    pkgs_list = _linux_cdm(['dpkg-query','-f',r'${Package} ${Version}\n','-W'])
    invent['host_pkgs_list'] = []
    for p in pkgs_list.split('\n'):
        n, v = p.split()
        invent['host_pkgs_list'].append({
            'name':n,
            'version':v
        })  


def _win_add_pass(invent:dict):
    invent['host_pkgs_list'] = []
    invent['host_users']=[]
    invent['host_netadapter_html'] = []
    invent["host_disk2stor_map"] = []

def _write_to_cache(data):
    cachedir = __salt__["config.get"]("cachedir")
    context_cache = cache.ContextCache({'cachedir':cachedir}, "inventorycache")
    context_cache.cache_context(data.copy())

def _read_from_cache():
    cachedir = __salt__["config.get"]("cachedir")
    try:
        context_cache = cache.ContextCache({'cachedir':cachedir}, "inventorycache")
        return context_cache.get_cache_context()
    except:
        return None

def _hash(dictionary:dict) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def _send_event(invent:dict):
    __salt__["event.send"](
            "custom/discovery/inventory/check",
            {"finished": True, "message": "audit result",'inventory':invent},
        )
        

def check(full=False, silent = False):
    '''
    launching audite
    '''
    invent = {}

    invent['host_os_family_lu'] = platform.system()
    invent["host_cpu_arch"] = platform.architecture()[0]

    if invent['host_os_family_lu'].startswith('Linux'):
        _linux_add_kernel(invent)
        _linux_add_version(invent)
        _linux_add_bios(invent)
        _linux_cpudata(invent)
        _linux_memdata(invent)
        _linux_host_disk2stor_map(invent)
        _linux_hostnames(invent)
        _linux_netatapter(invent)
        _linux_ip_address(invent)
        _linux_add_dns_servers(invent)
        _linux_add_users(invent)
        _linux_add_pkgs_list(invent)
    if invent['host_os_family_lu'].startswith('Windows'):
        _win_add_pass(invent)
    
    old_cache = _read_from_cache() 
    log.debug(f'old_cache : {old_cache}')
    old_cache_hash = None
    if old_cache:
        old_cache_hash = _hash(old_cache)  
    new_hash = _hash(invent)
    _write_to_cache(invent)
    invent['old_cache_hash'] = old_cache_hash
    invent['new_hash'] = new_hash
    if invent['new_hash'] != invent['old_cache_hash']:
        log.debug('new cache != old cache')     
    elif silent:
        return invent

    if not full:
        for key, val in invent.items():
            if isinstance(val,list):
                if len(val) > 1:
                    if isinstance(val[0],dict):
                        invent[key] = f'count {len(val)}'

    if invent:
        _send_event(invent)
    return invent

if __name__ == '__main__':
    print(check())