{% set run_sls = salt.pillar.get('run_sls') %}
salt.state:
  - tgt: "*"
  - sls:
    - {{run_sls}}
  - batch: 2
  - timeout: 10