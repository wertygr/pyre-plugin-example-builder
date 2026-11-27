import json
import os
import zipfile
from pathlib import Path

from plugins.plugin_tools.lib.base import base_destructor
from plugins.plugin_tools.plugin_types import CommandContext, PluginApi
from .schema import Meta, is_valid, Data
from .utils import is_blacklisted
from .cfg_v2 import cfg_parse

class BuildError(Exception):
    pass

def zipping(b_data: Data) -> None:
    with zipfile.ZipFile(b_data.out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("config.json", json.dumps(
            {
                "name": b_data.cfg["name"],
                "config": b_data.cfg["config"]
            }, indent=4)
                    )
        for file_path in b_data.files:
            path = Path(file_path)

            if not path.exists() or is_blacklisted(path, b_data.cfg["blacklist"]):
                continue

            if path.is_file():
                zf.write(path, arcname=path.name)

            elif path.is_dir():
                for root, dirs, filenames in os.walk(path):
                    root_path = Path(root)

                    dirs[:] = [d for d in dirs if not is_blacklisted(root_path / d, b_data.cfg["blacklist"])]

                    if root_path != path:
                        arcname = Path(path.name) / root_path.relative_to(path)
                        zf.write(root_path, arcname=arcname)

                    for filename in filenames:
                        item = root_path / filename
                        if not is_blacklisted(item, b_data.cfg["blacklist"]):
                            arcname = Path(path.name) / item.relative_to(path)
                            zf.write(item, arcname=arcname)


def search_config(cfg_file: Path) -> Meta | BuildError:
    if cfg_file.is_file() and cfg_file.exists():
        cfg = json.loads(cfg_file.read_text())
        is_cfg_valid = is_valid(cfg, Meta)
        if not is_cfg_valid:
            return BuildError("[search_config]: invalid config")
        return cfg
    return BuildError("[search_config]: Config not found or is dir")

def destructor(plugin_space: dict) -> None:
    base_destructor(__package__)

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict) -> None:
    data = api["data"]
    post = api["post"]

    if command_context["argc"] > 3:
        post("[builder::main]: not enough arguments", data)

    # build <path> <out_path>
    #  0      1       2
    path = Path(command_context["argv"][1])
    cfg = search_config(path)

    out = Path(command_context["argv"][2])
    if isinstance(cfg, BuildError):
        post(str(cfg), data)
        return

    b_data = Data(
        cfg=cfg,
        path=path,
        out=out
    )

    cfg_parse(b_data, api)
    zipping(b_data)