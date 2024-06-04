from custom_runners.minion_key_runner import MinionKey

def check_dns_resolve(remove_key: bool = True,timeout:int = 0):
    min_key = MinionKey(__opts__['pki_dir'])
    return min_key.check_dns_resolv(remove_key,timeout)