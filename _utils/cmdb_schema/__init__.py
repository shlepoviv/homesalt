"""
util for work with db
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from salt.utils.inventory_schema import Host,Host_disk2stor_map,Host_netadapter_html,Host_pkgs,Host_users

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

    def write_inventory(self,**data):
        """
        write inventory to db
        """
        if self.engine:       
            with Session(self.engine) as session:
                host = session.get(Host,data['id'])
                if host:
                    pass
                else:
                    list_attr = ['host_disk2stor_map',
                                'host_users',
                                'host_netadapter_html',
                                'host_pkgs_list']
                    host = Host(host_id=data['id'],**{k:v for k,v in data['data']['inventory'].items() if k not in list_attr})

                    for d in data['data']['inventory']['host_disk2stor_map']:
                        host.host_disk2stor_map.append(Host_disk2stor_map(**d))

                    for u in data['data']['inventory']['host_users']:
                        host.host_users.append(Host_users(**u))

                    for n in data['data']['inventory']['host_netadapter_html']:
                        host.host_netadapter_html.append(Host_netadapter_html(**n))

                    for p in data['data']['inventory']['host_pkgs_list']:
                        host.host_pkgs.append(Host_pkgs(**p))
                session.add(host)
                session.flush()
                session.commit()

