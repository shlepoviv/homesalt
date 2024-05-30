"""
An engine that reads messages from the salt event bus.

:configuration:

    Example configuration

    .. code-block:: yaml

        engines:
          - test_engine:
              # include_tags:
              #   - "*"
              exclude_tags:
                - salt/auth
                - minion_start
                - minion/refresh/*
                - "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]"
"""


import logging
import fnmatch



import salt.utils.event
import salt.utils.json

log = logging.getLogger(__name__)


def _match_tag(tag, include_tags, exclude_tags):
    """
    Match tag according to include and exclude lists
    """
    if include_tags:
        match = False
        for inc in include_tags:
            if fnmatch.fnmatch(tag, inc):
                match = True
                break
    else:
        match = True

    for exc in exclude_tags:
        if fnmatch.fnmatch(tag, exc):
            match = False
            break

    return match


def event_bus_context(opts):
    if opts["__role"] == "master":
        event_bus = salt.utils.event.get_master_event(
            opts, opts["sock_dir"], listen=True
        )
    else:
        event_bus = salt.utils.event.get_event(
            "minion",
            opts=opts,
            sock_dir=opts["sock_dir"],
            listen=True,
        )
    log.debug("test engine started")
    return event_bus


def start(include_tags=None, exclude_tags=None):

    include_tags = [] if include_tags is None else include_tags
    if not isinstance(include_tags, list):
        raise TypeError("include_tags is not a list")

    exclude_tags = [] if exclude_tags is None else exclude_tags
    if not isinstance(exclude_tags, list):
        raise TypeError("exclude_tags is not a list")
    
    with event_bus_context(__opts__) as event_bus:
        while True:
            event = event_bus.get_event(full=True)
            if event and _match_tag(event["tag"], include_tags, exclude_tags):
                jevent = salt.utils.json.dumps(event)
                __runners__["auditdb.write"](jevent)
                with open('/home/shlepov/log_test_engine','a') as f:
                    f.write(jevent+ "\n")
