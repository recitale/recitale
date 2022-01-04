import pytest
import subprocess
from unittest.mock import mock_open, patch

import recitale.utils


def test_cryptojs_openssl_compatible_encrypt():
    plaintext = b"this is a test"
    passphrase = "passphrase"
    encrypted = recitale.utils.cryptojs_openssl_compatible_encrypt(
        plaintext, passphrase
    )
    openssl = "openssl enc -d -base64 -A -aes-256-cbc -md md5 -pass pass:" + passphrase
    decrypted = subprocess.check_output(openssl.split(), input=encrypted)
    assert decrypted == plaintext


def test_remove_superficial_options():
    options = {
        "name": "test",
        "exif": 0x01,
        "text": "alt",
        "type": "video",
        "size": 12345678,
        "float": "left",
        "resize": "30%",
    }
    to_keep = {"test": 123, "something": "else"}
    options.update(to_keep)
    cleaned = recitale.utils.remove_superficial_options(options)

    assert cleaned == to_keep


class TestLoadSettings:
    def test_no_settings_yaml(self):
        with pytest.raises(SystemExit) as sysexit:
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    def test_bad_settings_yaml(self):
        with pytest.raises(SystemExit) as sysexit, patch(
            "builtins.open", mock_open(read_data="{}")
        ):
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    def test_empty_settings_yaml(self):
        with pytest.raises(SystemExit) as sysexit, patch(
            "builtins.open", mock_open(read_data="")
        ):
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    @patch("recitale.utils.yaml.safe_load", return_value=[])
    def test_not_dict_settings_yaml(self, mock_yaml):
        with pytest.raises(SystemExit) as sysexit, patch("builtins.open", mock_open()):
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    @patch("recitale.utils.yaml.safe_load", return_value={})
    def test_missing_title(self, mock_yaml):
        with pytest.raises(SystemExit) as sysexit, patch("builtins.open", mock_open()):
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    @patch(
        "recitale.utils.yaml.safe_load",
        return_value={"title": "test", "date": "01-01-1970"},
    )
    def test_bad_date_format(self, mock_yaml):
        with pytest.raises(SystemExit) as sysexit, patch("builtins.open", mock_open()):
            recitale.utils.load_settings(".")

        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    @patch("recitale.utils.yaml.safe_load", return_value={"title": "test"})
    def test_valid_settings(self, mock_yaml):
        with patch("builtins.open", mock_open()):
            settings = recitale.utils.load_settings(".")

        assert settings == {"title": "test"}
