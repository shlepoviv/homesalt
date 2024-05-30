reactor_all_tag:
  runner.auditdb:
    - name: write
    - arg:
        - {{ data|json }}