from custom_runners.minion_key_runner import MinionKey

def check_dns_resolve(remove_key: bool = True):
    min_key = MinionKey()
    return min_key(remove_key)