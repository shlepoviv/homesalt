# cat /opt/saltcmdb/modules/mem_leak.py
import sys
try:

    import psutil
    from datetime import datetime 

    procs=[]

    current_process = psutil.Process()

    def loging(mess):
        with open('/app/salt/var/log/salt/mem_leak.log','a')as f:
            f.write(f'{datetime.now()} | {mess}\n')

    for proc in psutil.process_iter():
        try:
            if 'mem_leak.py' in ' '.join(proc.cmdline()):
                if proc.pid == current_process.pid:
                    continue
                else:
                    psutil.sys.exit()
            if '/bin/salt-minion' in ' '.join(proc.cmdline()):
                if proc.pid != current_process.pid:
                    procs.append(proc)
        except psutil.ZombieProcess:
            pass

    loging(f'find {procs}')
    if procs:
        alloc_mem = int(sum([i.memory_info().rss for i in procs])/1024/1024)
        loging(f'procs mem: {alloc_mem}')
        if alloc_mem > 135:
            try:
                for proc in procs:
                    loging(f'kill proc {proc}')
                    proc.kill()
            except:
                pass
except Exception:
    sys.exit(1)