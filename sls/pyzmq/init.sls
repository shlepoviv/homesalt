{% if grains['kernel'] == 'Linux' %}
  {% set bin_env="/home/shlepov/.pyenv/versions/3.9.16/bin" %}
  {% set pyzmq_ver = salt['pip.list']('pyzmq',bin_env=bin_env)['pyzmq'] %}
  {% if pyzmq_ver|string == '25.1.2' %}

  wheel_cp:
    file.managed:
      - name: /tmp/pyzmq-23_2_0.whl
      - source: salt://sls/pyzmq/pyzmq-23_2_0.whl
      - replace: True

  # pyzmq_23:
  #   pip.installed:
  #     - name: /tmp/pyzmq-23.2.0.whl
  #     - force_reinstall: True
  #     - require:
  #       - module: wheel_cp
  {% else %}
  ok_s:
    test.succeed_without_changes:
      - name: 'pyzmq ver: {{pyzmq_ver|string}}'
  {% endif %}
{% endif %}