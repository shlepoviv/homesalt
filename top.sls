base:
  '*':
    - core
{% if grains['kernel'] == 'Linux' %}
    - firewall.{{grains['os_family']|lower}}
{% endif %}
  'os_family:Debian':
    - match: grain
    - pyinotify