from typing import Any, Optional, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY


class Base(DeclarativeBase):
    pass

class Host(Base):
    __tablename__ = 'host'

    host_id: Mapped[str] = mapped_column(primary_key=True)
    biosreleasedate: Mapped[str]
    host_bios_version: Mapped[str]

    host_cpu_arch: Mapped[str]
    host_cpu_core: Mapped[int]
    host_cpu_socket: Mapped[int]
    host_cpu_type: Mapped[str]

    host_ram: Mapped[int]
    swap_memory_size: Mapped[int]

    host_serial_number: Mapped[str]
    host_vendor: Mapped[str]
    hostname: Mapped[str]

    host_os_family_lu: Mapped[str]
    host_os_kernel: Mapped[str]
    host_os_kernel_full: Mapped[str]
    host_os_name: Mapped[str]
    host_os_release: Mapped[str]
    host_os_version: Mapped[str]

    host_dns_name: Mapped[str]

    host_ip_address: Mapped[str]

    host_model: Mapped[str]

    old_cache_hash: Mapped[str]
    new_hash: Mapped[str]

    host_dns_server: Mapped[list[str]] = mapped_column(ARRAY(String) )
    host_ip_addresses:  Mapped[list[str]] = mapped_column(ARRAY(String) )

    host_disk2stor_map: Mapped[List['Host_disk2stor_map']] = relationship(
        back_populates='host', cascade='all, delete-orphan'
    )

    host_users: Mapped[List['Host_users']] = relationship(
        back_populates='host', cascade="all, delete-orphan"
    )

    host_netadapter_html: Mapped[List['Host_netadapter_html']] = relationship(
        back_populates='host', cascade='all, delete-orphan'
    )

    host_pkgs_list: Mapped[List['Host_pkgs_list']] = relationship(
        back_populates='host', cascade="all, delete-orphan"
    )

    def __init__(self, **kwarg: Any): 
        list_obj_attr = ['host_disk2stor_map',
                                'host_users',
                                'host_netadapter_html',
                                'host_pkgs_list']
        list_columns = Base.metadata.tables.get('host').c.keys()
        list_columns.extend(list_obj_attr)
        
        host_disk2stor_map = kwarg['host_disk2stor_map'] if isinstance(
            kwarg['host_disk2stor_map'],list) else []
        for d in host_disk2stor_map:
            self.host_disk2stor_map.append(Host_disk2stor_map(**d))

        host_users = kwarg['host_users'] if isinstance(
            kwarg['host_users'],list) else []
        for u in host_users:
            self.host_users.append(Host_users(**u))

        host_netadapter_html = kwarg['host_netadapter_html'] if isinstance(
            kwarg['host_netadapter_html'],list) else []
        for n in host_netadapter_html:
            self.host_netadapter_html.append(Host_netadapter_html(**n))
        
        host_pkgs_list = kwarg['host_pkgs_list'] if isinstance(
            kwarg['host_pkgs_list'],list) else []
        for p in host_pkgs_list:
            self.host_pkgs_list.append(Host_pkgs_list(**p))           
        super().__init__(**{k:v for k,v in kwarg.items() if 
                       (k not in list_obj_attr) and (k in list_columns)})
        
    def get_diff(self,obj,list_attr=None):
        diff = {}
        list_columns = Base.metadata.tables.get('host').c.keys()
        if not list_attr:
            list_attr = list_columns
        for c in list_attr:
            if getattr(self,c) != getattr(obj,c):
                diff[c] = [getattr(self,c),getattr(obj,c)]
        return diff


class Host_users(Base):
    __tablename__ = 'host_users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[str] = mapped_column(ForeignKey('host.host_id'))
    host: Mapped['Host'] = relationship(back_populates='host_users')
    
    username: Mapped[str]
    uid: Mapped[int]
    gid: Mapped[int]
    home_dir: Mapped[str]
    shell: Mapped[str]

class Host_disk2stor_map(Base):
    __tablename__ = 'host_disk2stor_map'

    disk_id: Mapped[int] = mapped_column(primary_key=True) 
    host_id: Mapped[str] = mapped_column(ForeignKey('host.host_id'))
    host: Mapped['Host'] = relationship(back_populates='host_disk2stor_map')

    name: Mapped[str]
    serial: Mapped[str]
    vendor: Mapped[str]
    model: Mapped[str]
    size: Mapped[int]
    kname: Mapped[str]
    type: Mapped[str]
    mountpoint: Mapped[str]
    pkname: Mapped[str]
    kname: Mapped[str]

    # id_children: Mapped[List[int]] = mapped_column(ForeignKey('host_disk2stor_map.id')) 
    # children: Mapped[List['Host_disk2stor_map']] = relationship(
    #     back_populates='machine', cascade="all, delete-orphan"
    # )

    def __init__(self, **kwarg: Any):            
        if 'children' in kwarg:
            children = kwarg.pop('children')
            # self.children(Host_disk2stor_map(**children))
        super().__init__(**kwarg)

class Host_netadapter_html(Base):
    __tablename__ = 'host_netadapter_html'

    neadapter_id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[str] = mapped_column(ForeignKey('host.host_id'))
    host: Mapped['Host'] = relationship(back_populates='host_netadapter_html')

    name: Mapped[str]
    mac_address: Mapped[str]
    ips_info: Mapped[List['Ips_info']] = relationship(back_populates='host_netadapter_html',
                                                      cascade='all, delete-orphan')
    
    def __init__(self, **kwarg: Any):               
        if 'ips_info' in kwarg:
            for ips in kwarg.pop('ips_info'):
                self.ips_info.append(Ips_info(**ips))
        super().__init__(**kwarg)
            

class Ips_info(Base):
    __tablename__ = 'ips_info'

    ips_id: Mapped[int] = mapped_column(primary_key=True)
    host_id_netadapter_html: Mapped[int] = mapped_column(ForeignKey('host_netadapter_html.neadapter_id'))
    host_netadapter_html: Mapped['Host_netadapter_html'] = relationship(back_populates='ips_info')

    ip: Mapped[str]
    netmask: Mapped[str]
    network: Mapped[str]
    alias: Mapped[str]

class Host_pkgs_list(Base):
    __tablename__ = 'host_pkgs_list'

    host_pkg_id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[str] = mapped_column(ForeignKey('host.host_id'))
    host: Mapped['Host'] = relationship(back_populates='host_pkgs_list')

    name: Mapped[str]
    version: Mapped[str]

