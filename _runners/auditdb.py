"""
writes audit result to the base
"""
import logging

from cmdb_schema import WorkWithDB
from tracem import TraceM

log = logging.getLogger(__name__)
import salt.utils.json

def write(data):
    log.debug('try write to db')
    jevent = salt.utils.json.dumps(data)
    with open('/home/shlepov/log_test_engine','a') as f:
        f.write(jevent+ "\n")
    return True
