import logging
import shlex
import subprocess

from json import dumps as json_dumps
from pathlib import Path
from zlib import crc32

from .utils import remove_superficial_options


logger = logging.getLogger("recitale." + __name__)


class VideoCommon:
    @property
    def ratio(self):
        # For when BaseVideo.ratio is called before BaseVideo.copy() is.
        if not self.size:
            if VideoFactory.global_options["binary"] == "ffmpeg":
                binary = "ffprobe"
            else:
                binary = "avprobe"
            command = (
                binary
                + " -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "
                + shlex.quote(str(self.filepath))
            )
            out = subprocess.check_output(shlex.split(command))
            width, height = out.decode("utf-8").split(",")
            self.size = width, height
        else:
            width, height = self.size
        return width / height


class Thumbnail(VideoCommon):
    suffix = ".jpg"

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
            suffix=self.suffix,
        )

        return p.parent / (p.stem + suffix)


class Reencode(Thumbnail):
    def __init__(self, base_filepath, base_id, size, extension):
        self.suffix = "." + extension
        super().__init__(base_filepath, base_id, size)


class BaseVideo(VideoCommon):
    def __init__(self, options, global_options):
        self.thumbnails = dict()
        self.reencodes = dict()
        self.options = global_options.copy()
        self.options.update(options)
        self.filepath = self.options["name"]
        self.options = remove_superficial_options(self.options)
        self.chksum_opt = crc32(
            bytes(json_dumps(self.options, sort_keys=True), "utf-8")
        )

    def reencode(self, size):
        reencode = Reencode(
            self.filepath, self.chksum_opt, size, self.options["extension"]
        )
        return self.reencodes.setdefault(reencode.filepath, reencode).filepath.name

    def thumbnail(self, size):
        thumbnail = Thumbnail(self.filepath, self.chksum_opt, size)
        return self.thumbnails.setdefault(thumbnail.filepath, thumbnail).filepath.name


# TODO: add support for looking into parent directories (name: ../other_gallery/pic.jpg)
class VideoFactory:
    base_vids = dict()
    global_options = dict()

    @classmethod
    def get(cls, path, video):
        vid = video.copy()
        # To resolve paths with .. in them, we need to resolve the path first and then
        # find the relative path to the source (current) directory.
        vid["name"] = Path(path).joinpath(vid["name"]).resolve().relative_to(Path.cwd())
        bvid = BaseVideo(vid, cls.global_options)
        return cls.base_vids.setdefault(bvid.filepath / str(bvid.chksum_opt), bvid)
