import pytest

from json import dumps as json_dumps
from unittest.mock import patch
from zlib import crc32

from recitale.image import BaseImage, ImageFactory
from recitale.utils import remove_superficial_options


class TestBaseImage:
    @patch("recitale.image.imagesize.get", return_value=(200, 300))
    def test_first_copy_no_resize(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg"}, {})
        base.copy()
        assert base.copysize == (200, 300)

    @patch("recitale.image.imagesize.get", return_value=(200, 300))
    def test_two_copies_no_resize(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg"}, {})
        base.copy()
        base.copy()
        assert len(base.thumbnails.keys()) == 1

    @patch("recitale.image.imagesize.get", return_value=(200, 300))
    def test_copy_resize(self, mock_imgsz):
        base = BaseImage({"name": "test.jpg", "resize": "50%"}, {})
        base.copy()
        assert base.copysize == (100, 150)

    @patch("recitale.image.imagesize.get", return_value=(200, 300))
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
    @patch("recitale.image.imagesize.get", return_value=(200, 300))
    def test_copy_filepath_remove_superficial_options(
        self, mock_imgsz, mock_rm_sup_opt
    ):
        base = BaseImage({"name": "test.jpg", "resize": "50%", "test": "test123"}, {})
        copy = base.copy()
        mock_rm_sup_opt.called_once_with(
            {"name": "test.jpg", "resize": "50%", "test": "test123"}
        )
        assert copy == "test-%s-100x150.jpg" % (
            crc32(bytes(json_dumps({"test": "test123"}, sort_keys=True), "utf-8"))
        )

    @patch("recitale.image.imagesize.get", return_value=(200, 300))
    def test_copy_invalid_resize(self, mock_imgsz, caplog):
        base = BaseImage({"name": "test.jpg", "resize": "50"}, {})
        with pytest.raises(SystemExit) as sysexit:
            base.copy()
            assert sysexit.type == SystemExit
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
        assert sysexit.type == SystemExit
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
