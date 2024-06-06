{% if grains['kernel'] == 'Linux' %}:
copy_mem_leak:
  file.managed:
    - name: /app/salt/modules/mem_leak.py
    - source: salt://skrips/mem_leak.py
    - makedirs: True
    - replace: True
{% endif %}