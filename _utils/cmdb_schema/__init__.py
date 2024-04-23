"""
util for work with db
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from inventory_schema import Host

log = logging.getLogger(__name__)

_DB_PARAM = 'postgresql+psycopg2://postgres:d34gj8h9qNn@192.168.1.13/cmdb'

class WorkWithDB():
    def __init__(self):
        self._get_engine()
        self._init_table()

    def _get_engine(self):
        try:
            engine = create_engine(_DB_PARAM)            
            self.engine = engine
        except Exception as e:
            log.error(f'util cmdb_schema: can not create engine - {e}')
    
    def _init_table(self):
        Host.metadata.create_all(self.engine)

    def write_inventory(self,data):
        """
        write inventory to db
        """
        if self.engine:       
            with Session(self.engine) as session:
                host = session.get(Host,data['id'])
                if host:
                    log.debug(f'write_inventory: find {data["id"]} host in base')
                    updatehost = Host(host_id=data['id'],**data['data']['inventory'])
                    if host.get_diff(updatehost):
                        log.debug(f'write_inventory: find {data["id"]} host in base with different attributes')
                    else:
                        log.debug(f'write_inventory: find {data["id"]} host in base')
                else:
                    host = Host(host_id=data['id'],**data['data']['inventory'])
                session.add(host)
                session.flush()
                session.commit()
                log.debug(f'write_inventory: {data["id"]} host create in base')

