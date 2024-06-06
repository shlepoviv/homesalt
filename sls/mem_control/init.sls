{% if grains['kernel'] == 'Linux' %}
{% set pythonexecutable = salt['config.get']('pythonexecutable') %}
copy_mem_leak:
  file.managed:
    - name: /app/salt/modules/mem_leak.py
    - source: salt://sls/mem_control/mem_leak.py
    - makedirs: True
    - replace: True


mem_leak_check:
  schedule.present:
    - function: cmd.run
    - job_args:
      - "{{ pythonexecutable }} mem_leak.py || echo can not start mem_leak >> /app/salt/var/log/salt/mem_leak_error.log"
      - /app/salt/modules/
    - seconds: 60
    - return_job: false
    - jid_include: false
    - enabled: true
    - maxrunning: 1

{% endif %}