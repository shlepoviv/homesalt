{% set tag = salt.pillar.get('event_tag') %}
{% set data = salt.pillar.get('event_data') %}
write:
  salt.runner:
    - name: auditdb.write
    - arg:
        - {{ data }}