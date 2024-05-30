"""
writes audit result to the base
"""
import logging

from cmdb_schema import WorkWithDB
from tracem import TraceM

log = logging.getLogger(__name__)


def write(data):
    log.debug('try write to db')
    tr = TraceM()
    db = WorkWithDB()
    db.write_inventory(data)
    tr.dumptrace()
    return True
