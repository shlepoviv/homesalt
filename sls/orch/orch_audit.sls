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
        success: False
    - onfail:
      - salt: run_audit

send_success_event_test:
  salt.runner:
    - name: event.send
    - tag: result_test
    - data:
        success: True
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
        success: False
    - onfail:
      - salt: run_audit

send_success_event_run_audit:
  salt.runner:
    - name: event.send
    - tag: result_run_audit
    - data:
        success: True
    - require:
      - salt: run_audit