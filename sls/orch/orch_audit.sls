{% set kwargs_audit = {'batch' : 2, 'timeout': 20} %}

testrun:
  salt.runner:
    - name: test.stream

testfail:
  salt.runner:
    - name: test.fail

send_failure_event_test:
  salt.runner:
    - name: event.send
    - tag: result_test
    - data:
        {{kwargs_audit}}
    - onfail:
      - salt: run_audit

send_success_event_test:
  salt.runner:
    - name: event.send
    - tag: result_test
    - data:
        {{kwargs_audit}}
    - require:
      - salt: testrun
          
run_audit:
  salt.state:
    - tgt: "*"
    - sls:
      - sls.audit
    - kwargs: {{kwargs_audit}}
    - require:
      - salt: testrun

send_failure_event_run_audit:
  salt.runner:
    - name: event.send
    - tag: result_run_audit
    - data:
        {{kwargs_audit}}
    - onfail:
      - salt: run_audit

send_success_event_run_audit:
  salt.runner:
    - name: event.send
    - tag: result_run_audit
    - data:
        {{kwargs_audit}}
    - require:
      - salt: run_audit