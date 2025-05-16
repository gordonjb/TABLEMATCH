import dataclasses
import os
from pathlib import Path
import click
import yaml
import logging
from parse import parse_show
import json

logger = logging.getLogger(__name__)

DEFAULT_LEVEL = logging.WARNING


@click.command()
@click.argument("filename", type=click.File(mode="r"))
@click.argument(
    "destination",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
@click.option(
    "--loglevel",
    type=click.Choice(list(logging.getLevelNamesMapping())),
    default=logging.getLevelName(DEFAULT_LEVEL),
    show_default=True,
    help="Set the Python logging level.",
)
def main(filename, destination, loglevel):
    """
    Parse path FILENAME, outputting YAML representations of the shows
    in folder DESTINATION, which will be created if it does not
    exist. Existing files will be overwritten if they clash.
    """
    logging.basicConfig(level=loglevel)

    out_path = Path(destination)
    out_path.mkdir(parents=True, exist_ok=True)

    shows = yaml.safe_load(filename)

    for show in shows:
        show_obj = parse_show(show)
        filename = "-".join(show_obj.id) + ".json"
        with open(os.path.join(out_path, filename), "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(show_obj), f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
