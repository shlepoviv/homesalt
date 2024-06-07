{% if grains['kernel'] == 'Linux' %}
  {% set pyzmq_wheel="pyzmq-23.2.0-pp39-pypy39_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl" %}
  {% set bin_env="/home/shlepov/.pyenv/versions/3.9.16/bin" %}
  {% set pyzmq_ver = salt['pip.list']('pyzmq',bin_env=bin_env)['pyzmq'] %}
  {% if pyzmq_ver|string == '25.1.2' %}
  

  wheel_cp:
    file.managed:
      - name: /tmp/{{pyzmq_wheel}}
      - source: salt://sls/pyzmq/{{pyzmq_wheel}}
      - replace: True

  pyzmq_23:
    pip.installed:
      - name: /tmp/{{pyzmq_wheel}}
      - force_reinstall: True
      - require:
        - file: wheel_cp

  wheel_remove:
    module.run:
      - file.remove:
        - path: /tmp/{{pyzmq_wheel}}
        - require:
          - pip: pyzmq_23
  {% else %}
  ok_s:
    test.succeed_without_changes:
      - name: 'pyzmq ver: {{pyzmq_ver|string}}'
  {% endif %}
{% endif %}