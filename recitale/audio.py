import logging

from json import dumps as json_dumps
from pathlib import Path
from zlib import crc32

from .utils import remove_superficial_options


logger = logging.getLogger("recitale." + __name__)


class Reencode:
    def __init__(self, base_filepath, base_id, extension):
        self.filepath = self.__filepath(base_filepath, base_id, "." + extension)

    def __filepath(self, base_filepath, base_id, extension):
        p = Path(base_filepath)
        suffix = "-{base_id}{suffix}".format(
            base_id=base_id,
            suffix=extension,
        )

        return p.parent / (p.stem + suffix)


class BaseAudio:
    def __init__(self, filepath, global_options):
        self.reencodes = dict()
        self.options = global_options.copy()
        self.filepath = filepath
        self.options = remove_superficial_options(self.options)
        self.chksum_opt = crc32(
            bytes(json_dumps(self.options, sort_keys=True), "utf-8")
        )

    def reencode(self):
        reencode = Reencode(self.filepath, self.chksum_opt, self.options["extension"])
        return self.reencodes.setdefault(reencode.filepath, reencode).filepath.name


# TODO: add support for looking into parent directories (name: ../other_gallery/pic.jpg)
class AudioFactory:
    base_audios = dict()
    global_options = dict()

    @classmethod
    def get(cls, path, filepath):
        # To resolve paths with .. in them, we need to resolve the path first and then
        # find the relative path to the source (current) directory.
        filepath = Path(path).joinpath(filepath).resolve().relative_to(Path.cwd())
        baud = BaseAudio(filepath, cls.global_options)
        return cls.base_audios.setdefault(baud.filepath / str(baud.chksum_opt), baud)
