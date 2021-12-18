import logging
import sys
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Hash import MD5
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad
from email.utils import formatdate
from datetime import datetime
from builtins import str

from pathlib import Path
import ruamel.yaml as yaml


logger = logging.getLogger("recitale." + __name__)


def remove_superficial_options(options):
    cleaned_options = options.copy()
    if "name" in cleaned_options:
        del cleaned_options["name"]
    if "exif" in cleaned_options:
        del cleaned_options["exif"]
    if "text" in cleaned_options:
        del cleaned_options["text"]
    if "type" in cleaned_options:
        del cleaned_options["type"]
    if "size" in cleaned_options:
        del cleaned_options["size"]
    if "float" in cleaned_options:
        del cleaned_options["float"]
    # "resize" only applies to image.copy() in templates, no need to propagate it to the cache since
    # the actual size of the "copy" thumbnail is part of the filename and will trigger a
    # regeneration if changed (thus "resize" setting is appropriately watched without regenerating
    # non-copy thumbnails).
    if "resize" in cleaned_options:
        del cleaned_options["resize"]
    return cleaned_options


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    fmt_nok = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s"
    fmt_ok = "%(asctime)s %(levelname)s - %(message)s"

    FORMATS = {
        logging.INFO: OKGREEN + fmt_ok + ENDC,
        logging.WARNING: WARNING + fmt_nok + ENDC,
        logging.ERROR: FAIL + fmt_nok + ENDC,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def makeform(template, settings, gallery_settings):
    from_template = template.get_template("form.html")
    form = base64.b64encode(
        from_template.render(settings=settings, gallery=gallery_settings).encode(
            "Utf-8"
        )
    )
    return str(form, "utf-8")


def evp_bytestokey(hash_class, salt, passphrase, iterations, key_size):
    """
    Python implementation of key and IV derivation from passphrase
    as implemented in OpenSSL EVP_BytesToKey, c.f.
    https://github.com/openssl/openssl/blob/38fc02a7084438e384e152effa84d4bf085783c9/crypto/evp/evp_key.c#L78-L154
    """
    block = None
    key = b""

    while len(key) < key_size:
        hasher = hash_class.new()
        if block:
            hasher.update(block)
        hasher.update(passphrase)
        hasher.update(salt)
        block = hasher.digest()
        for i in range(iterations - 1):
            block = hash_class.new(block).digest()
        key = key + block

    return key


def cryptojs_openssl_compatible_encrypt(plaintext, passphrase):
    # CryptoJS is only capable of reading this very specific AES-256-CBC encrypted
    # content with key and IV derivation from OpenSSL specific implementation.
    # Moreover, it needs to follow OpenSSL specific format which is the following:
    # Base64 encoded string of:
    # - ASCII representation of "Salted__" (8 bytes)
    # - salt (8 bytes)
    # - AES-256-CBC encrypted content
    #
    # The key and IV used to encrypt the content are derived from a passphrase
    # by using the salt and the OpenSSL specific derivation called
    # EVP_BytesToKey. The key is 32-byte long for AES-256 and the IV is 16-byte
    # long for CBC.

    salt = get_random_bytes(8)
    keyiv = evp_bytestokey(MD5, salt, bytes(passphrase, "utf-8"), 1, 32 + 16)
    iv = keyiv[32 : 32 + 16]
    key = keyiv[:32]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(plaintext, AES.block_size))
    return base64.b64encode("Salted__".encode("ascii") + salt + encrypted_data)


def encrypt(password, template, gallery_path, settings, gallery_settings):
    encrypted_template = template.get_template("encrypted.html")
    index_plain = Path("build").joinpath(gallery_path, "index.html")

    with open(index_plain, "rb") as f:
        encrypted = cryptojs_openssl_compatible_encrypt(f.read(), password)

    html = encrypted_template.render(
        settings=settings,
        form=makeform(template, settings, gallery_settings),
        ciphertext=str(encrypted, "utf-8"),
        gallery=gallery_settings,
    ).encode("Utf-8")
    return html


def rfc822(date):
    epoch = datetime.utcfromtimestamp(0).date()
    return formatdate((date - epoch).total_seconds())


def load_settings(folder):
    try:
        with open(
            Path(".").joinpath(folder, "settings.yaml").resolve(), "r"
        ) as settings:
            gallery_settings = yaml.safe_load(settings.read())
    except (yaml.error.MarkedYAMLError, yaml.YAMLError) as exc:
        msg = "There is something wrong in %s/settings.yaml" % folder
        if isinstance(exc, yaml.error.MarkedYAMLError):
            msg = msg + str(exc.context_mark)
        logger.error(msg)
        sys.exit(1)
    except ValueError:
        logger.error(
            "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml", folder
        )
        sys.exit(1)
    except Exception as exc:
        logger.exception(exc)
        sys.exit(1)

    if gallery_settings is None:
        logger.error("The %s/settings.yaml file is empty", folder)
        sys.exit(1)
    elif not isinstance(gallery_settings, dict):
        logger.error("%s/settings.yaml should be a dict", folder)
        sys.exit(1)
    elif "title" not in gallery_settings:
        logger.error("You should specify a title in %s/settings.yaml", folder)
        sys.exit(1)

    if gallery_settings.get("date"):
        try:
            datetime.strptime(str(gallery_settings.get("date")), "%Y-%m-%d")
        except ValueError:
            logger.error(
                "Incorrect data format, should be YYYY-MM-DD in %s/settings.yaml",
                folder,
            )
            sys.exit(1)
    return gallery_settings
