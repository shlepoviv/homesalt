"""
writes audit result to the base
"""
import logging

from cmdb_schema import WorkWithDB

log = logging.getLogger(__name__)

def write(data): 
    db = WorkWithDB()
    db.write_inventory(data)
    return True