run_audit:
  salt.state:
    - tgt: "*"
    - sls:
      - sls.audit
    - batch: 2
    - timeout: 20