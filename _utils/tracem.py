import tracemalloc
import linecache
from pathlib import Path

FIRST_SNAP = '/etc/tracem/fsnap'
LAST_SNAP = '/etc/tracem/lsnap'
class TraceM():
    @staticmethod
    def start():
        tracemalloc.start()
    @staticmethod
    def printdiff(s1,s2):
        top_stats = s1.compare_to(s2, 'lineno')

        print("[ Top 5 differences ]")
        for stat in top_stats[:5]:
            print(stat)
    @staticmethod
    def display_top(snapshot=None, key_type='lineno', limit=10):
        if not snapshot:
            snapshot = tracemalloc.Snapshot.load(LAST_SNAP)    

        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        ))
        top_stats = snapshot.statistics(key_type)

        print("Top %s lines" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            print("#%s: %s:%s: %.1f KiB"
                % (index, frame.filename, frame.lineno, stat.size / 1024))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))
    @staticmethod
    def dumptrace():
        snap = tracemalloc.take_snapshot()
        if Path(FIRST_SNAP).exists():
            snap.dump(LAST_SNAP)  
        else: 
            snap.dump(FIRST_SNAP)   