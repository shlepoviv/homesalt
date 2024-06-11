{% set conf_file = salt['config.get']('conf_file') %}

sshd_config_harden:
    file.keyvalue:
      - name: {{conf_file}}_test
      - key_values:
          master: 
            - 192.168.1.12
            - 192.168.1.13
          root_dir: '/app/salt'
          log_level_logfile: 'all'
      - separator: ' '
      - uncomment: '# '
      - key_ignore_case: True
      - append_if_not_found: True
