"""
util for work with db
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from inventory_schema import Host


    
_DB_PARAM = 'postgresql+psycopg2://postgres:d34gj8h9qNn@192.168.1.13/cmdb'


class WorkWithDB():
    def __init__(self):
        self._get_engine()

    def _get_engine(self):
        try:
            engine = create_engine(_DB_PARAM)
            self.engine = engine
        except Exception as e:
            log.error(f'util cmdb_schema: can not create engine - {e}')

    def init_table(self):
        Host.metadata.create_all(self.engine)

    def write_inventory(self, data):
        """
        write inventory to db
        """
        
        if self.engine:
            with Session(self.engine) as session:
                log.error(f'work with db data {str(data)}')
                host = Host(host_id=data['id'], **data['data']['inventory'])
                upgreded_host = session.merge(host)
                session.commit()
