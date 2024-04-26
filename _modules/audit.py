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

log = logging.getLogger(__name__)


def _linux_cdm(cmd: list[str], timeout: int = 3):
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT) as proc:

        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subprocess.SubprocessError as e:
            proc.kill()
            log.debug(f'audit _linux_cdm: {e}')
            log.debug(f'audit _linux_cdm: {e}')
            return 'None'
    return outs.decode('utf-8').rstrip()


def _linux_add_kernel(invent: dict):

    invent["host_os_release"] = _linux_cdm(['uname', '-r'])
    invent["host_os_kernel"] = _linux_cdm(['uname', '-v'])
    invent["host_os_kernel_full"] = _linux_cdm(['uname', '-a'])


def _linux_add_version(invent: dict):

    host_os_par = {"NAME": "host_os_name",
                   "VERSION_ID": "host_os_version"
                   }
    file_version = '/etc/os-release'
    if os.path.exists(file_version):
        with open(file_version, "r", encoding='utf-8') as f:
            regex = re.compile(r"^([\w]+)=(?:'|\")?(.*?)(?:'|\")?(\\n)?$")
            for line in f:
                match = regex.match(line.strip())
                if match:
                    if match.group(1) in host_os_par:
                        invent[host_os_par[match.group(1)]] = re.sub(
                            r'\\([$"\'\\`])', r"\1", match.group(2)
                        )
    else:
        log.debug(f'audit: file {file_version} is not exist')


def _linux_add_bios(invent: dict):
    host_os_par = {
        "host_bios_version": "bios_version",
        "biosreleasedate": "bios_date",
        "host_serial_number": "product_serial",
        'host_model': 'board_name',
        'host_vendor': 'board_vendor'
    }
    for key, fw_file in host_os_par.items():
        contents_file = os.path.join("/sys/class/dmi/id", fw_file)
        if os.path.exists(contents_file):
            with open(contents_file, "r") as ifile:
                invent[key] = ifile.read().strip()
        else:
            log.debug(f'audit: file /sys/class/dmi/id/{fw_file} is not exist')


def _linux_cpudata(invent: dict):
    file_cpuinfo = '/proc/cpuinfo'
    if os.path.exists(file_cpuinfo):
        invent["host_cpu_core"] = 0
        physical_id = set()
        with open(file_cpuinfo, 'r', encoding='utf-8') as f:
            for line in f:
                par = line.strip().split(':')

                if len(par) == 2:
                    key = par[0].strip()
                    val = par[1].strip()
                    if key == 'processor':
                        invent['host_cpu_core'] += 1
                    elif key == 'physical id':
                        physical_id.add(val)
                    elif key == 'model name':
                        invent["host_cpu_type"] = val

        invent["host_cpu_socket"] = len(physical_id)
    else:
        log.debug(f'audit: file /sys/class/dmi/id/{file_cpuinfo} is not exist')


def _linux_memdata(invent: dict):
    file_meminfo = '/proc/meminfo'
    host_mem_par = {
        'MemTotal': 'host_ram',
        'SwapTotal': 'swap_memory_size'
    }
    if os.path.exists(file_meminfo):
        with open(file_meminfo, 'r', encoding='utf-8') as f:
            for line in f:
                par = line.strip().split(':')

                if len(par) == 2:
                    key = par[0].strip()
                    val = par[1].strip()
                    if key in host_mem_par:
                        invent[host_mem_par[key]] = int(val.split()[0]) // 1024
    else:
        log.debug(f'audit: file /sys/class/dmi/id/{file_meminfo} is not exist')


def _linux_host_disk2stor_map(invent: dict):
    def convert_size(disk: dict):
        if 'size' in disk:
            disk['size'] = int(disk['size']) // 1024 // 1024
        if 'children' in disk:
            for c in disk['children']:
                convert_size(c)

    def _replace_hex_escaped(s):
        r = s.string[s.regs[0][0]+2:s.regs[0][1]]
        r = chr(int((r), 16))
        return r

    def _parse_parm(line):
        i = 0
        start = 0
        res = {}
        for par in list_param:
            while line[i] != ' ' and i < len(line)-1:
                i += 1
            if start == i:
                res[par] = None
            else:
                res[par] = re.sub(r'\\x[0-9A-Fa-f][0-9A-Fa-f]',
                                  _replace_hex_escaped, line[start:i])
            i += 1
            start = i
        return res

    list_param = ['name', 'serial', 'vendor', 'model',
                  'size', 'type', 'mountpoint', 'pkname', 'kname']
    out1 = _linux_cdm(['lsblk', '-n', '-io', 'name']).split('\n')
    out2 = _linux_cdm(['lsblk', '-n', '-r', '-ibo',
                      ','.join(list_param)]).split('\n')

    res = []
    list_parent = []
    prevlvl = 0
    for line, line2 in zip(out1, out2):
        i = 0
        while line[i] in (' ', '`', '|', '-'):
            i += 1
        lvl = i//2
        if lvl == 0:
            res.append(_parse_parm(line2))
            list_parent.clear()
            prevlvl = 0
        else:
            if prevlvl < lvl:
                if not list_parent:
                    list_parent.append(res[-1])
                else:
                    list_parent.append(list_parent[-1]['children'][-1])
                list_parent[-1]['children'] = [_parse_parm(line2)]
                prevlvl = lvl
            elif prevlvl == lvl:
                list_parent[-1]['children'].append(_parse_parm(line2))
            elif prevlvl > lvl:
                for _ in range(prevlvl - lvl):
                    list_parent.pop()
                list_parent[-1]['children'].append(_parse_parm(line2))
                prevlvl = lvl

    for disk in res:
        convert_size(disk)

    invent["host_disk2stor_map"] = res


def _linux_hostnames(invent: dict):
    invent['host_dns_name'] = _linux_cdm(['hostname', '-f'])
    invent['hostname'] = _linux_cdm(['hostname', '-s'])


def _linux_netatapter(invent: dict):
    out = _linux_cdm(['ip', 'a']).splitlines()

    pattern = re.compile(r'^\d*:\s*([^:]+)\s*:\s*<.+>')

    list_adapt = []

    adapt = None

    for line in out:
        m = pattern.search(line)
        if m:
            if adapt:
                list_adapt.append(adapt)
            adapt = {'name': m.group(1),
                     'ips_info': []}
        else:
            if adapt:
                sline = line.split()

                if sline[0].startswith('link'):
                    adapt['mac_address'] = sline[1]

                elif sline[0].startswith('inet'):

                    if '/' in sline[1]:
                        ip, pref = sline[1].split('/')
                    else:
                        ip = sline[1]
                        pref = 32

                    i = ipaddress.ip_interface(f'{ip}/{pref}')

                    adapt['ips_info'].append({"ip": str(i.ip),
                                              "netmask": str(i.netmask),
                                              "network": str(i.network),
                                              "alias": sline[-1] 
                                              if not sline[0].startswith('inet6') else None})

    if adapt:
        list_adapt.append(adapt)

    invent['host_netadapter_html'] = list_adapt


def _linux_ip_address(invent: dict):
    invent['host_ip_address'] = _linux_cdm(['hostname', '-i'])
    out = _linux_cdm(['hostname', '-I']).split()
    out.append(invent['host_ip_address'])
    invent['host_ip_addresses'] = out


def _linux_add_dns_servers(invent: dict):
    file_meminfo = '/run/systemd/resolve/resolv.conf'
    invent['host_dns_server'] = []
    if os.path.exists(file_meminfo):
        with open(file_meminfo, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('nameserver'):
                    invent['host_dns_server'].append(line.split()[1])
    else:
        log.debug(f'audit: file {file_meminfo} is not exist')


def _linux_add_users(invent: dict):
    file_meminfo = '/etc/passwd'
    invent['host_users'] = []
    if os.path.exists(file_meminfo):
        with open(file_meminfo, 'r', encoding='utf-8') as f:
            for line in f:
                u = line.split(':')
                invent['host_users'].append({
                    "username": u[0],
                    "uid": u[2],
                    "gid": u[3],
                    "home_dir": u[4],
                    "shell": u[5]

                })
    else:
        log.debug(f'audit: file {file_meminfo} is not exist')


def _linux_add_pkgs_list(invent: dict):
    pkgs_list = _linux_cdm(
        ['dpkg-query', '-f', r'${Package} ${Version}\n', '-W'])
    invent['host_pkgs_list'] = []
    for p in pkgs_list.split('\n'):
        n, v = p.split()
        invent['host_pkgs_list'].append({
            'name': n,
            'version': v
        })


def _win_add_pass(invent: dict):
    invent['host_pkgs_list'] = []
    invent['host_users'] = []
    invent['host_netadapter_html'] = []
    invent["host_disk2stor_map"] = []


def _write_to_cache(dictionary: dict):
    cachedir = __opts__["cachedir"]
    cache_path = os.path.join(cachedir, 'discovering', 'inventory')
    if not os.path.isdir(os.path.dirname(cache_path)):
        os.mkdir(os.path.dirname(cache_path))
    with open(cache_path, "w") as cache:
        json.dump(dictionary, cache)


def _read_from_cache():
    cachedir = __opts__["cachedir"]
    cache_path = os.path.join(cachedir, 'discovering', 'inventory')
    res = None
    if os.path.exists(cache_path):
        with open(cache_path, "r") as cache:
            res = json.load(cache)
    return res


def _hash(dictionary: dict, collapse=False) -> str:
    """MD5 hash each item of a dictionary."""
    def _get_h(s: str):
        dhash = hashlib.md5()
        dhash.update(s.encode())
        return dhash.hexdigest()

    if collapse:
        return _get_h(json.dumps(dictionary, sort_keys=True))
    else:
        res = {}
        for key, val in dictionary.items():
            if isinstance(val, str):
                res[key] = _get_h(val)
            else:
                res[key] = _get_h(json.dumps(val, sort_keys=True))
        return res


def _send_event(invent: dict):
    __salt__["event.send"](
        "custom/discovery/inventory/check",
        {"finished": True, "message": "audit result", 'inventory': invent},
    )


def check(full=False, silent=False):
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
    old_cache_hash = None
    if old_cache:
        old_cache_hash = _hash(old_cache, collapse=True)
    new_cache = _hash(invent)
    _write_to_cache(new_cache)
    new_cache_hash = _hash(new_cache, collapse=True)

    invent['old_cache_hash'] = old_cache_hash
    invent['new_hash'] = new_cache_hash

    if old_cache_hash:
        if invent['new_hash'] != invent['old_cache_hash']:
            if not full:
                for key in new_cache:
                    if new_cache[key] == old_cache.get(key, None):
                        del invent[key]
        elif silent:
            return invent

    if invent:
        _send_event(invent)
    return invent


if __name__ == '__main__':
    print(check())
