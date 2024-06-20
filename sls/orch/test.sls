{% set kwargs_audit = {'batch' : 2, 'timeout': 20} %}

send_failure_event_test:
  salt.runner:
    - name: event.send
    - tag: result_test
    - data:
        {{kwargs_audit}}

send_success_event_test:
  salt.runner:
    - name: event.send
    - tag: result_test
    - data:
        foo: bar
        success: True
