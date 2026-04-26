import pytest

from json import dumps as json_dumps
from unittest.mock import patch
from zlib import crc32

from PIL import Image

from recitale.image import BaseImage, ImageFactory
from recitale.utils import remove_superficial_options


class TestBaseImage:
    @pytest.mark.parametrize("exif", [None, {0x0112: 1}, {0x0112: 5}])
    @pytest.mark.parametrize("auto_orient", [False, True])
    @patch("recitale.image.Image.open")
    def test_first_copy_no_resize(self, mock_imgsz, auto_orient, exif):
        def mock_exif():
            return exif

        type(mock_imgsz.return_value).size = (200, 400)
        mock_imgsz.return_value.getexif.side_effect = mock_exif

        base = BaseImage({"name": "test.jpg"}, {"auto-orient": auto_orient})
        base.copy()
        ratio = base.ratio

        # .ratio should have not called Image.open() again
        mock_imgsz.assert_called_once()

        if not auto_orient:
            mock_imgsz.return_value.getexif.assert_not_called()
            assert base.size == (200, 400)
            assert base.copysize == (200, 400)
            assert ratio == 200 / 400
            return

        mock_imgsz.return_value.getexif.assert_called_once()
        if exif and exif.get(0x112, 1) == 5:
            assert base.size == (400, 200)
            assert base.copysize == (400, 200)
            assert ratio == 400 / 200
            return

        assert base.size == (200, 400)
        assert base.copysize == (200, 400)
        assert ratio == 200 / 400

    @patch("recitale.image.Image.open")
    def test_ratio_first(self, mock_imgsz):
        type(mock_imgsz.return_value).size = (200, 400)

        base = BaseImage({"name": "test.jpg"}, {"auto-orient": False})
        ratio = base.ratio
        mock_imgsz.return_value.getexif.assert_not_called()
        assert base.size == (200, 400)
        assert ratio == 200 / 400

        mock_imgsz.reset_mock()

        base.copy()

        # BaseImage.copy() shouldn't need to inspect the file after .ratio
        mock_imgsz.assert_not_called()

    @patch("recitale.image.Image.open", return_value=Image.new("L", (200, 300)))
    def test_two_copies_no_resize(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg"}, {})
        base.copy()
        base.copy()
        assert len(base.thumbnails.keys()) == 1

    @patch("recitale.image.Image.open", return_value=Image.new("L", (200, 300)))
    def test_copy_resize(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg", "resize": "50%"}, {})
        base.copy()
        assert base.size == (200, 300)
        assert base.copysize == (100, 150)

    @patch("recitale.image.Image.open", return_value=Image.new("L", (200, 300)))
    def test_copy_filepath(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg", "resize": "50%"}, {})
        copy = base.copy()
        assert copy == "test-%s-100x150.jpg" % (
            crc32(bytes(json_dumps({}, sort_keys=True), "utf-8"))
        )

    @patch(
        "recitale.image.remove_superficial_options",
        side_effect=remove_superficial_options,
    )
    @patch("recitale.image.Image.open", return_value=Image.new("L", (200, 300)))
    def test_copy_filepath_remove_superficial_options(
        self, mock_imgsz, mock_rm_sup_opt
    ):
        base = BaseImage({"name": "test.jpg", "resize": "50%", "test": "test123"}, {})
        copy = base.copy()
        mock_rm_sup_opt.assert_called_once_with(
            {"name": "test.jpg", "resize": "50%", "test": "test123"}
        )
        assert copy == "test-%s-100x150.jpg" % (
            crc32(bytes(json_dumps({"test": "test123"}, sort_keys=True), "utf-8"))
        )

    @patch("recitale.image.Image.open", return_value=Image.new("L", (200, 300)))
    def test_copy_invalid_resize(self, mock_imgsz, caplog):
        base = BaseImage({"name": "test.jpg", "resize": "50"}, {})
        with pytest.raises(SystemExit) as sysexit:
            base.copy()
            assert sysexit.type is SystemExit
            assert sysexit.value.code == 1
            assert (
                caplog.text == "(test.jpg) specified resize setting is not a percentage"
            )


# HACK because ImageFactory.base_imgs does not seem to be reset between tests.
@pytest.fixture
def factory():
    yield
    ImageFactory.base_imgs = dict()


@pytest.mark.usefixtures("factory")
# End HACK
class TestImageFactory:
    def test_diff_paths_diff_images(self):
        img1 = ImageFactory.get("gallery1", "test1.jpg")
        img2 = ImageFactory.get("gallery2", "test2.jpg")
        assert img1 != img2

    def test_same_path_diff_images(self):
        img1 = ImageFactory.get("gallery", "test1.jpg")
        img2 = ImageFactory.get("gallery", "test2.jpg")
        assert img1 != img2

    def test_diff_paths_same_image(self):
        img1 = ImageFactory.get("gallery1", "test.jpg")
        img2 = ImageFactory.get("gallery2", "test.jpg")
        assert img1 != img2

    def test_same_image_with_without_name(self):
        img1 = ImageFactory.get("gallery", "test.jpg")
        img2 = ImageFactory.get("gallery", {"name": "test.jpg"})
        assert img1 is img2

    def test_image_dict_without_name(self):
        with pytest.raises(SystemExit) as sysexit:
            ImageFactory.get("gallery", {"notname": "test.jpg"})
        assert sysexit.type is SystemExit
        assert sysexit.value.code == 1

    def test_same_path_same_image(self):
        img1 = ImageFactory.get("gallery", "test.jpg")
        img2 = ImageFactory.get("gallery", "test.jpg")
        assert img1 is img2

    def test_same_path_same_image_one_base_imgs(self):
        ImageFactory.get("gallery", "test.jpg")
        ImageFactory.get("gallery", "test.jpg")
        base_imgs = ImageFactory.base_imgs
        assert len(base_imgs.keys()) == 1

    @pytest.mark.parametrize("gallery", ["gallery", "light/../gallery"])
    @pytest.mark.parametrize("image", ["test.jpg", "light/../test.jpg"])
    def test_dotdot_paths(self, gallery, image):
        img1 = ImageFactory.get("gallery", "test.jpg")
        img2 = ImageFactory.get(gallery, image)
        assert img1 is img2

    def test_base_imgs_presence(self):
        img1 = ImageFactory.get("gallery", "test.jpg")
        base_imgs = ImageFactory.base_imgs
        assert len(base_imgs.keys()) == 1
        assert img1 is list(base_imgs.values())[0]
