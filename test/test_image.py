import pytest

from recitale.image import ImageFactory


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
        assert img1 == img2

    def test_image_dict_without_name(self):
        with pytest.raises(SystemExit) as sysexit:
            ImageFactory.get("gallery", {"notname": "test.jpg"})
        assert sysexit.type == SystemExit
        assert sysexit.value.code == 1

    def test_same_path_same_image(self):
        img1 = ImageFactory.get("gallery", "test.jpg")
        img2 = ImageFactory.get("gallery", "test.jpg")
        assert img1 == img2

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
        assert img1 == img2

    def test_base_imgs_presence(self):
        img1 = ImageFactory.get("gallery", "test.jpg")
        base_imgs = ImageFactory.base_imgs
        assert len(base_imgs.keys()) == 1
        assert img1 == list(base_imgs.values())[0]
