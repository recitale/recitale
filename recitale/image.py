import logging
import re
import sys
import urllib.parse

from json import dumps as json_dumps
from pathlib import Path
from PIL import Image
from zlib import crc32

from .utils import remove_superficial_options


logger = logging.getLogger("recitale." + __name__)


class Thumbnail:
    def __init__(self, base_filepath, base_id, size):
        self.filepath = self.__filepath(base_filepath, base_id, size)
        self.size = size

    def __filepath(self, base_filepath, base_id, size):
        p = Path(base_filepath)
        width, height = size
        suffix = "-{base_id}-{width}x{height}{suffix}".format(
            base_id=base_id,
            width=width if width else "",
            height=height if height else "",
            suffix=p.suffix,
        )

        return p.parent / (p.stem + suffix)


class BaseImage:
    re_rsz = re.compile(r"^(\d+)%$")

    def __init__(self, options, global_options):
        # Rotation applied to self.size, self.copysize dimensions already
        self.copysize = None
        self.thumbnails = dict()
        self.options = global_options.copy()
        self.options.update(options)
        self.filepath = self.options["name"]
        self.resize = self.options.get("resize")
        self.options = remove_superficial_options(self.options)
        self.chksum_opt = crc32(
            bytes(json_dumps(self.options, sort_keys=True), "utf-8")
        )

    def copy(self):
        if not self.copysize:
            self._init_size()
            width, height = self.size

            if self.resize:
                match = BaseImage.re_rsz.match(str(self.resize))
                if not match:
                    logger.error(
                        "(%s) specified resize setting is not a percentage",
                        self.filepath,
                    )
                    sys.exit(1)
                percentage = int(match.group(1))
                width, height = width * percentage // 100, height * percentage // 100

            self.copysize = width, height

        return self.thumbnail(self.copysize)

    def _add_thumbnail(self, thumbnail):
        return self.thumbnails.setdefault(thumbnail.filepath, thumbnail)

    def thumbnail(self, size):
        thumbnail = Thumbnail(self.filepath, self.chksum_opt, size)
        return urllib.parse.quote(self._add_thumbnail(thumbnail).filepath.name)

    @property
    def ratio(self):
        self._init_size()

        return self.size[0] / self.size[1]

    def _init_size(self):
        if hasattr(self, "size"):
            return

        im = Image.open(self.filepath)
        self.size = im.size

        rotated = False

        if not self.options.get("auto-orient", False):
            return

        exif = im.getexif()
        if not exif:
            return

        rotated = exif.get(0x0112, 1) in {5, 6, 7, 8}
        if rotated:
            self.size = (self.size[1], self.size[0])


# TODO: add support for looking into parent directories (name: ../other_gallery/pic.jpg)
class ImageFactory:
    base_imgs = dict()
    global_options = dict()

    @classmethod
    def get(cls, path, image):
        if not isinstance(image, dict):
            image = {"name": image}

        if "name" not in image:
            logger.error(
                'At least one image in "%s" does not have a `name` property, please add the '
                "filename of the image to a `name` property.",
                path + "/settings.yaml",
            )
            sys.exit(1)

        im = image.copy()
        # To resolve paths with .. in them, we need to resolve the path first and then
        # find the relative path to the source (current) directory.
        im["name"] = Path(path).joinpath(im["name"]).resolve().relative_to(Path.cwd())
        img = BaseImage(im, cls.global_options)
        return cls.base_imgs.setdefault(img.filepath / str(img.chksum_opt), img)
