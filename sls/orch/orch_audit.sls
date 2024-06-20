testrun:
  salt.runner:
    - name: test.stream

testfail:
  salt.function:
    - name: file.copy

send_failure_event:
  salt.runner:
    - name: event.send
    - tag: failure/test
    - data:
        fail: testfail
    - onfail:
      - salt: testfail

run_audit:
  salt.state:
    - tgt: "*"
    - sls:
      - sls.audit
    - batch: 2
    - timeout: 20
    - require:
      - salt: testrun

send_failure_event_run_audit:
  salt.runner:
    - name: event.send
    - tag: failure/run_audit
    - data:
        baz: qux
    - onfail:
      - salt: run_audit
