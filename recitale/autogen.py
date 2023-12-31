import logging
import os
import sys
from time import gmtime, strftime, strptime
from jinja2 import Template
from pathlib import Path
from PIL import Image

from .utils import load_settings

DATA = """title: {{ title }}
date: {{ date }}
cover: {{ cover }}
sections:
  - type: pictures-group
    images:
      -
{% set nb = namespace(value=range(2,5)|random) %}
{% set count = namespace(value=0) %}
{% for file in files %}
         - {{ file.name }}
{% if count.value != nb.value %}
{% set count.value = count.value + 1 %}
{% elif not loop.last %}
      -
{% set count.value = 0 %}
{% set nb. value = range(2,5)|random %}
{% endif %}
{% endfor %}
"""

logger = logging.getLogger("recitale." + __name__)

types = ("*.JPG", "*.jpg", "*.JPEG", "*.jpeg", "*.png", "*.PNG")

TIME_FORMAT = "%Y:%m:%d %H:%M:%S"


def get_exif(filename):
    exif = Image.open(filename).getexif()
    if exif is not None:
        # DateTimeOriginal, DateTimeDigitized, DateTime(DateTimeModified)
        ctime = exif.get(0x9003, exif.get(0x9004, exif.get(0x0132)))
        if ctime is not None:
            return ctime

    return strftime(TIME_FORMAT, gmtime(os.path.getmtime(filename)))


def build_template(folder, force):
    files_grabbed = []

    gallery_settings = load_settings(folder)

    if "static" in gallery_settings:
        logger.info("Skipped: Nothing to do in %s gallery", folder)
        return

    if "title" not in gallery_settings:
        logger.error("%s/settings.yaml: 'title' setting missing", folder)
        sys.exit(1)

    if "sections" in gallery_settings and force is not True:
        logger.info("Skipped: %s gallery is already generated", folder)
        return

    for files in types:
        files_grabbed.extend(Path(folder).glob(files))
    template = Template(DATA, trim_blocks=True)

    files = sorted(files_grabbed, key=get_exif)

    cover = gallery_settings.get("cover", files[0].name)
    date = gallery_settings.get("date")
    if not date:
        date_from_exif = strptime(get_exif(files[0]), TIME_FORMAT)
        date = strftime("%Y-%m-%d", date_from_exif)

    msg = template.render(
        title=gallery_settings["title"],
        date=date,
        cover=cover,
        files=files,
    )
    Path(folder).joinpath("settings.yaml").write_text(msg)
    logger.info("Generation: %s gallery", folder)


def autogen(folder=None, force=False):
    if folder:
        build_template(folder, force)
        return

    for settings in Path(".").rglob("settings.yaml"):
        # Ignore "root" settings.yaml
        if settings.samefile(Path(".").joinpath("settings.yaml")):
            continue
        folder = settings.parent
        if not list(Path(folder).glob("*/**/settings.yaml")):
            build_template(folder, force)
