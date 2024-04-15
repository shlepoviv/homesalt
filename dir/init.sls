/etc/dev/file_needed_dev:
  file.managed:
    - source: salt://dir/file_needed_dev
    - makedirs: True