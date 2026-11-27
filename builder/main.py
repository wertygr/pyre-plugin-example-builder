import argparse as arg
import json
import os
import zipfile
from pathlib import Path

from plugins.plugin_tools.lib.base import base_destructor
from plugins.plugin_tools.plugin_types import CommandContext, PluginApi
from .schema import Meta, is_valid
from .utils import fake_post, is_blacklisted
from .cfg_v2 import cfg_parse

class BuildError(Exception):
    pass

class PluginArgumentParser(arg.ArgumentParser):
    def error(self, message: str):
        raise ValueError(f"error: {message}")

    def exit(self, status=0, message=None):
        if message:
            print(message)

def zipping(files: list[Path], cfg: Meta, out: Path, args: arg.Namespace, api: PluginApi) -> None:
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("config.json", json.dumps(
            {
                "name": cfg["name"],
                "config": cfg["config"]
            }, indent=4)
                    )
        for file_path in files:
            path = Path(file_path)

            if not path.exists() or is_blacklisted(path, cfg["blacklist"]):
                continue

            if path.is_file():
                zf.write(path, arcname=path.name)

            elif path.is_dir():
                for root, dirs, filenames in os.walk(path):
                    root_path = Path(root)

                    dirs[:] = [d for d in dirs if not is_blacklisted(root_path / d, cfg["blacklist"])]

                    if root_path != path:
                        arcname = Path(path.name) / root_path.relative_to(path)
                        zf.write(root_path, arcname=arcname)

                    for filename in filenames:
                        item = root_path / filename
                        if not is_blacklisted(item, cfg["blacklist"]):
                            arcname = Path(path.name) / item.relative_to(path)
                            zf.write(item, arcname=arcname)


def search_config(list_file: list[Path]) -> dict | BuildError:
    for i, it in enumerate(list_file):
        if it.is_file() and it.name == "plugin.json":
            cfg = json.loads(it.read_text())
            is_cfg_valid = is_valid(cfg, Meta)
            if not is_cfg_valid:
                return BuildError("[search_config]: invalid config")
            cfg["__path"] = it.resolve().parent
            del list_file[i]  # del cfg file
            return cfg
    return BuildError("[search_config]: 'plugin.json' not found")


parser = PluginArgumentParser()
parser.add_argument("--cfg-v2", action="store_true", help="cfg v2 file")
parser.add_argument("objects", nargs="+", type=Path, help="input file/directory")
parser.add_argument("-o", "--output", required=True, help="output file(zip format)")


def destructor(plugin_space: dict) -> None:
    base_destructor(__package__)

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict) -> None:
    if not api:
        data = api["data"] = None
        post = api["data"] = fake_post
    else:
        data = api["data"]
        post = api["post"]

    args = parser.parse_args(command_context["argv"][1:])

    cfg = search_config(args.objects)
    if isinstance(cfg, BuildError):
        post(str(cfg), data)
        return
    if args.cfg_v2:
        cfg_parse(args.objects, cfg, api)
    zipping(args.objects, cfg, args.output, args, api)