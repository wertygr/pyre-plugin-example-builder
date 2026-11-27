from pathlib import Path

from builder.schema import Meta
from plugins.plugin_tools.plugin_types import PluginApi


def cfg_parse(files: list[Path], cfg: Meta, api: PluginApi) -> None:
    data = api["data"]
    post = api["post"]
    if not "src" in cfg:
        post("[zipping]: not 'src' in cfg", data)
        return
    for i, it in enumerate(cfg["src"]):
        obj = cfg["__path"] / Path(it)
        if not isinstance(it, str):
            post(f"[zipping]: cfg['src'][{i}] is {type(it)}", data)
            return
        if not obj.exists():
            post(f"[zipping]: cfg['src'][{i}]({obj.resolve().parent}) is not exist", data)
            return
        files.append(obj)