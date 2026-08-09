from vidsift.config.models import JSRuntimesConfig


def get_js_runtimes_config(config: list[JSRuntimesConfig]) -> dict:
    runtimes_lookup: dict = {}
    for runtime in config:
        runtimes_lookup[runtime.name] = {"path": runtime.path}

    return runtimes_lookup
