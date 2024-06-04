from pathlib import Path
import time

class MinionKey:

    def __init__(self, pki_dir: str):
        self.pki_path = Path(pki_dir, 'minions')

    def delete_key(self, lost: list):
        for minion_id in lost:
            try:
                Path(self.pki_path, minion_id).unlink()
            except:
                pass

    def check_dns_resolv(self, remove_key: bool = True, timeout: int = 0):
        import socket

        res = []
        for min_key in self.pki_path.glob('*'):
            min_id = min_key.name
            time.sleep(timeout)
            try:
                print(socket.gethostbyname(min_id))
            except OSError:
                res.append(min_id)
        if remove_key:
            self.delete_key(res)

        return res
