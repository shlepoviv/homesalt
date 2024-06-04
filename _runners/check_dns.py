import socket
from pathlib import Path

def check_minions(remove_key:bool=True):
    pki_dir = Path(__opts__['pki_dir'],'minions')
    res = []
    for min_key in pki_dir.glob('*'):
        min_id = min_key.name
        try:
            print(socket.gethostbyname(min_id))
        except OSError:
            res.append(min_id)
    return res


if __name__ == '__main__':
    print(check_minions())
