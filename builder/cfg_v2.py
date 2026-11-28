from pathlib import Path

from .schema import Data
from plugins.plugin_tools.plugin_types import PluginApi


from plugins.plugin_tools.lib.base import PluginExit

def cfg_parse(b_data: Data, api: PluginApi) -> None:
    data = api["data"]
    post = api["post"]
    for i, it in enumerate(b_data.cfg["src"]):
        if not isinstance(it, str):
            post(f"[cfg_parse]: cfg['src'][{i}] is {type(it)}", data)
            raise PluginExit()
        obj = b_data.path.resolve().parent / Path(it)
        
        if not obj.exists():
            post(f"[cfg_parse]: cfg['src'][{i}]({obj.resolve().parent}) is not exist", data)
            raise PluginExit()
        b_data.files.append(obj)