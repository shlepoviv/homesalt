{% if grains['kernel'] == 'Linux' %}
copy_mem_leak:
  file.managed:
    - name: /app/salt/modules/mem_leak.py
    - source: salt://sls/mem_control/mem_leak.py
    - makedirs: True
    - replace: True
{% endif %}

mem_leak_check:
  schedule.present:
    - function: cmd.run
    - job_args:
      - 'python mem_leak.py'
      - /app/salt/modules/
    - seconds: 60
    - return_job: false
    - jid_include: false
    - enabled: true
    - maxrunning: 1