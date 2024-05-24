runorch:
  runner.state.orchestrate:
    - args:
        - mods: sls.orch.customreact
        - pillar:
            event_tag: {{ tag }}
            event_data: {{ data|json }}