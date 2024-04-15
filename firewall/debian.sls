{% set roles = grains['roles']|default([]) %}

flushrule:
  iptables.flush: []

lo:
  iptables.insert:
    - position: 1
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - in-interface: lo
    - save: True

established:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - match: state
    - connstate: ESTABLISHED,RELATED
    - save: True

ssh:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - match: state
    - connstate: NEW
    - dport: 22
    - protocol: tcp
    - save: True

salt:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - match: state
    - connstate: NEW
    - dport: 4505:4506
    - protocol: tcp
    - save: True

{% if 'pgsqlserver' in roles or 'pgsqluser' in roles %}
postgres:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - match: state
    - connstate: NEW
    - dport: 5432
    - protocol: tcp
    - save: True
{% endif %}

dropinput:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: DROP