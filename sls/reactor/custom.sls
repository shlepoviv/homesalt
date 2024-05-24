runorch:
  runner.state.orchestrate:
    - args:
        - mods: orch.customreact
        - pillar:
            event_tag: {{ tag }}
            event_data: {{ data|json }}