{% if grains['kernel'] == 'Linux' %}
  {% set pyzmq_wheel="pyzmq-23.2.0-cp39-cp39-manylinux_2_12_x86_64.manylinux2010_x86_64.whl" %}
  {% set bin_env="/home/shlepov/.pyenv/versions/3.9.16/bin" %}
  {% set pyzmq_ver = salt['pip.list']('pyzmq',bin_env=bin_env)['pyzmq'] %}
  {% if pyzmq_ver|string != '23.2.0' %}
  wheel_cp:
    file.managed:
      - name: /tmp/{{pyzmq_wheel}}
      - source: salt://sls/pyzmq/{{pyzmq_wheel}}
      - replace: True

  unistall_pyzmq_25:
    module.run:
      - pip.uninstall:
        - pkgs: pyzmq
        - bin_env: {{bin_env}}
      - require:
        - file: wheel_cp

  install_pyzmq_23:
    module.run:
      - pip.install:
        - pkgs: /tmp/{{pyzmq_wheel}}
        - bin_env: {{bin_env}}
        - force_reinstall: True
        - ignore_installed: True
      - require:
        - module: unistall_pyzmq_25

  wheel_remove:
    module.run:
      - file.remove:
        - path: /tmp/{{pyzmq_wheel}}
      - require:
        - module: install_pyzmq_23
  {% else %}
  ok_s:
    test.succeed_without_changes:
      - name: 'already pyzmq ver: {{pyzmq_ver|string}}'
  {% endif %}
{% else %}
  ok_s:
    test.succeed_without_changes:
      - name: 'not linux' 
{% endif %}