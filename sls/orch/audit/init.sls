run_sync_all:
  module.run:
    - name: saltutil.sync_all

# deep_reload:
#   module.run:
#     - name: reload_utils.deep_reload
#     - require:
#         - module: run_sync_all

audit_run:
  module.run:
    - name: audit.check
    - require:
      # - module: deep_reload
      - module: run_sync_all