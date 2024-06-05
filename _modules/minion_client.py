

def memory():
    """
    Return memory using salt-minion
    """
    try:
        import psutil
    except Exception:
         return 'Can not inport psutil'
    procs=[]

    current_process = psutil.Process()

    for proc in psutil.process_iter():
        try:
            if '/bin/salt-minion' in ' '.join(proc.cmdline()):
                # if proc.pid != current_process.pid:
                    procs.append(proc)
        except psutil.ZombieProcess:
            pass

    alloc_mem = 0        
    if procs:
        alloc_mem = int(sum([i.memory_info().rss for i in procs])/1024/1024)
    return {'All poroc':alloc_mem, 'Current process': current_process.memory_info().rss}

