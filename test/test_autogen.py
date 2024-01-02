import pytest
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory
import logging

import recitale.autogen


class TestAutogen:
    @pytest.mark.parametrize("force", [True, False])
    def test_folder_force(self, force):
        with patch("recitale.autogen.build_template"):
            recitale.autogen.autogen(".", force)
            recitale.autogen.build_template.assert_called_once_with(".", force)

    def test_folder_no_force(self):
        with patch("recitale.autogen.build_template"):
            recitale.autogen.autogen(".")
            recitale.autogen.build_template.assert_called_once_with(".", False)

    def test_all_folders_exclude_root(self):
        def only_replace_cwd(arg):
            directory = get_temp_dir() if arg == "." else arg
            return Path(directory)

        with patch(
            "recitale.autogen.build_template"
        ), TemporaryDirectory() as td, patch(
            "recitale.autogen.Path", side_effect=only_replace_cwd
        ):

            def get_temp_dir():
                return td

            root = Path(td).joinpath("settings.yaml")
            root.touch()
            recitale.autogen.autogen()
            assert not any(
                root in args for args in recitale.autogen.build_template.call_args_list
            )

    def test_all_folders_exclude_with_subgalleries(self):
        def only_replace_cwd(arg):
            directory = get_temp_dir() if arg == "." else arg
            return Path(directory)

        with patch(
            "recitale.autogen.build_template"
        ), TemporaryDirectory() as td, patch(
            "recitale.autogen.Path", side_effect=only_replace_cwd
        ):

            def get_temp_dir():
                return td

            root = Path(td).joinpath("settings.yaml")
            gallery = Path(td).joinpath("gallery")
            subgallery = gallery.joinpath("subgallery")
            subgallery.mkdir(parents=True)
            gallery_settings = gallery.joinpath("settings.yaml")
            subgallery_settings = subgallery.joinpath("settings.yaml")
            root.touch()
            gallery_settings.touch()
            subgallery_settings.touch()
            recitale.autogen.autogen()
            assert not any(
                root in args for args in recitale.autogen.build_template.call_args_list
            )
            assert not any(
                gallery_settings in args
                for args in recitale.autogen.build_template.call_args_list
            )
            recitale.autogen.build_template.assert_called_once_with(subgallery, False)

    def test_all_folders_exclude_with_subsubgalleries(self):
        def only_replace_cwd(arg):
            directory = get_temp_dir() if arg == "." else arg
            return Path(directory)

        with patch(
            "recitale.autogen.build_template"
        ), TemporaryDirectory() as td, patch(
            "recitale.autogen.Path", side_effect=only_replace_cwd
        ):

            def get_temp_dir():
                return td

            root = Path(td).joinpath("settings.yaml")
            gallery = Path(td).joinpath("gallery")
            subgallery = gallery.joinpath("subgallery")
            subsubgallery = subgallery.joinpath("subsubgallery")
            subsubgallery.mkdir(parents=True)
            gallery_settings = gallery.joinpath("settings.yaml")
            subgallery_settings = subgallery.joinpath("settings.yaml")
            subsubgallery_settings = subsubgallery.joinpath("settings.yaml")
            root.touch()
            gallery_settings.touch()
            subgallery_settings.touch()
            subsubgallery_settings.touch()
            recitale.autogen.autogen()
            assert not any(
                root in args for args in recitale.autogen.build_template.call_args_list
            )
            assert not any(
                gallery_settings in args
                for args in recitale.autogen.build_template.call_args_list
            )
            assert not any(
                subgallery_settings in args
                for args in recitale.autogen.build_template.call_args_list
            )
            recitale.autogen.build_template.assert_called_once_with(
                subsubgallery, False
            )


class TestBuildTemplate:
    @patch("recitale.autogen.load_settings", return_value={"static": True})
    def test_static(self, p, caplog):
        caplog.set_level(logging.INFO)
        recitale.autogen.build_template(".", False)
        assert "Skipped: Nothing to do in" in caplog.text

    def test_missing_required_title(self, caplog):
        with pytest.raises(SystemExit) as sysexit, patch(
            "recitale.autogen.load_settings", return_value={}
        ):
            recitale.autogen.build_template(".", False)
        assert ": 'title' setting missing" in caplog.text
        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    @patch(
        "recitale.autogen.load_settings",
        return_value={
            "title": "test",
            "cover": "test.jpg",
            "date": "20230610",
            "sections": [],
        },
    )
    def test_existing_gallery(self, p, caplog):
        caplog.set_level(logging.INFO)
        recitale.autogen.build_template(".", False)
        assert " gallery is already generated" in caplog.text

    @patch(
        "recitale.autogen.load_settings",
        return_value={"title": "test", "cover": "test.jpg"},
    )
    @patch("recitale.autogen.get_exif", return_value="2023:06:10 10:10:10")
    def test_missing_date(self, patch_exif, patch_load):
        with TemporaryDirectory() as td:
            f = "test.png"
            Path(td).joinpath(f).touch()
            recitale.autogen.build_template(td, False)
            generated = Path(td).joinpath("settings.yaml")
            assert generated.exists()
            with open(generated) as content:
                assert (
                    "".join(content.readlines())
                    == f"""title: test
date: 2023-06-10
cover: test.jpg
sections:
  - type: pictures-group
    images:
      -
         - {f}
"""
                )

    @patch(
        "recitale.autogen.load_settings",
        return_value={"title": "test", "date": "20230610"},
    )
    @patch("recitale.autogen.get_exif", return_value="2023:06:10 10:10:10")
    def test_missing_cover(self, patch_exif, patch_load):
        with TemporaryDirectory() as td:
            f = "test.png"
            Path(td).joinpath(f).touch()
            recitale.autogen.build_template(td, False)
            generated = Path(td).joinpath("settings.yaml")
            assert generated.exists()
            with open(generated) as content:
                assert (
                    "".join(content.readlines())
                    == f"""title: test
date: 20230610
cover: {f}
sections:
  - type: pictures-group
    images:
      -
         - {f}
"""
                )

    @patch(
        "recitale.autogen.load_settings",
        return_value={"title": "test", "date": "20230610"},
    )
    @patch(
        "recitale.autogen.get_exif",
        side_effect=["2023:06:10 10:10:10", "2016:10:08 01:01:01"],
    )
    def test_missing_cover_oldest_picked(self, patch_exif, patch_load):
        with TemporaryDirectory() as td:
            f = "test.png"
            Path(td).joinpath(f).touch()
            fold = "test-oldest.png"
            Path(td).joinpath(fold).touch()
            recitale.autogen.build_template(td, False)
            generated = Path(td).joinpath("settings.yaml")
            assert generated.exists()
            with open(generated) as content:
                assert (
                    "".join(content.readlines())
                    == f"""title: test
date: 20230610
cover: {fold}
sections:
  - type: pictures-group
    images:
      -
         - {fold}
         - {f}
"""
                )

    @patch(
        "recitale.autogen.load_settings",
        return_value={"title": "test", "cover": "test.jpg", "date": "20230610"},
    )
    @patch("recitale.autogen.get_exif", return_value="2023:06:10 10:10:10")
    @pytest.mark.parametrize("filext", recitale.autogen.types)
    def test_file_extensions(self, patch_exif, patch_load, filext):
        with TemporaryDirectory() as td:
            f = "test" + filext[1:]
            Path(td).joinpath(f).touch()
            recitale.autogen.build_template(td, False)
            generated = Path(td).joinpath("settings.yaml")
            assert generated.exists()
            with open(generated) as content:
                assert (
                    "".join(content.readlines())
                    == f"""title: test
date: 20230610
cover: test.jpg
sections:
  - type: pictures-group
    images:
      -
         - {f}
"""
                )

    @patch(
        "recitale.autogen.load_settings",
        return_value={
            "title": "test",
            "cover": "test.jpg",
            "date": "20230610",
            "sections": [],
        },
    )
    @patch("recitale.autogen.get_exif", return_value="2023:06:10 10:10:10")
    def test_overwrite_existing(self, patch_exif, patch_load):
        with TemporaryDirectory() as td:
            f = "test.JPG"
            Path(td).joinpath(f).touch()
            recitale.autogen.build_template(td, True)
            generated = Path(td).joinpath("settings.yaml")
            assert generated.exists()
            with open(generated) as content:
                assert (
                    "".join(content.readlines())
                    == """title: test
date: 20230610
cover: test.jpg
sections:
  - type: pictures-group
    images:
      -
         - test.JPG
"""
                )


class TestGetExif:
    @patch("recitale.autogen.os.path.getmtime", return_value=1635362648.7638042)
    def test_no_exif(self, patched_getmtime):
        with patch("recitale.autogen.Image.open") as p:
            p.return_value.getexif.return_value = None
            assert (
                recitale.autogen.get_exif("example/first_gallery/stuff.png")
                == "2021:10:27 19:24:08"
            )

    @patch("recitale.autogen.os.path.getmtime", return_value=1635362648.7638042)
    def test_no_datetime_exifs(self, patched_getmtime):
        assert (
            recitale.autogen.get_exif("example/first_gallery/stuff.png")
            == "2021:10:27 19:24:08"
        )

    @pytest.mark.parametrize("exif", [0x9003, 0x9004, 0x0132])
    def test_datetime_exifs(self, exif):
        with patch("recitale.autogen.Image.open") as p:
            p.return_value.getexif.return_value = {exif: "2023:06:10 10:10:10"}
            assert (
                recitale.autogen.get_exif("example/first_gallery/stuff.png")
                == "2023:06:10 10:10:10"
            )
