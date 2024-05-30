reactor_all_tag:
  salt.runner:
    - name: auditdb.write
    - arg:
        - {{ data|json }}