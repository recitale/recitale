import pytest

from json import dumps as json_dumps
from pathlib import Path
from unittest.mock import patch
from zlib import crc32

from recitale.video import BaseVideo, VideoFactory
from recitale.utils import remove_superficial_options


class TestVideoCommon:
    check_output = '{ "streams": [{ "height": 480, "width": 840}], "format": {"duration": "10.4"} }'

    def test_ratio_base(self):
        VideoFactory.global_options = {"binary": "ffmpeg", "extension": "webm"}
        bvid = BaseVideo({"name": "test.mp4"}, VideoFactory.global_options)
        with patch(
            "recitale.video.subprocess.check_output", return_value=self.check_output
        ):
            assert bvid.ratio == 840 / 480

    def test_ratio_base_only_one_subprocess(self):
        VideoFactory.global_options = {"binary": "ffmpeg", "extension": "webm"}
        bvid = BaseVideo({"name": "test.mp4"}, VideoFactory.global_options)
        with patch(
            "recitale.video.subprocess.check_output", return_value=self.check_output
        ):
            assert bvid.ratio == 840 / 480
        assert bvid.ratio == 840 / 480

    def test_ratio_reencode(self):
        VideoFactory.global_options = {"binary": "ffmpeg", "extension": "webm"}
        bvid = BaseVideo({"name": "test.mp4"}, VideoFactory.global_options)
        with patch(
            "recitale.video.subprocess.check_output", return_value=self.check_output
        ):
            revid_path = bvid.reencode((840, 480))
            revid = bvid.reencodes.get(Path(revid_path))
        assert revid.ratio == 840 / 480

    def test_duration_base(self):
        VideoFactory.global_options = {"binary": "ffmpeg", "extension": "webm"}
        bvid = BaseVideo({"name": "test.mp4"}, VideoFactory.global_options)
        with patch(
            "recitale.video.subprocess.check_output", return_value=self.check_output
        ):
            assert bvid.duration == 10.4

    def test_duration_base_only_one_subprocess(self):
        VideoFactory.global_options = {"binary": "ffmpeg", "extension": "webm"}
        bvid = BaseVideo({"name": "test.mp4"}, VideoFactory.global_options)
        with patch(
            "recitale.video.subprocess.check_output", return_value=self.check_output
        ):
            assert bvid.duration == 10.4
        assert bvid.duration == 10.4


class TestBaseVideo:
    def test_baseid(self):
        base = BaseVideo({"name": "test.mp4", "some": "options"}, {})
        assert base.chksum_opt == crc32(
            bytes(json_dumps({"some": "options"}, sort_keys=True), "utf-8")
        )

    @patch(
        "recitale.video.remove_superficial_options",
        side_effect=remove_superficial_options,
    )
    def test_baseid_removed_superficial_opt(self, mock_rm_sup_opt):
        base1 = BaseVideo({"name": "test.mp4", "some": "options", "resize": "50%"}, {})
        mock_rm_sup_opt.assert_called_with(
            {"name": "test.mp4", "some": "options", "resize": "50%"}
        )
        base2 = BaseVideo({"name": "test.mp4", "some": "options"}, {})
        mock_rm_sup_opt.assert_called_with({"name": "test.mp4", "some": "options"})
        assert base1.chksum_opt == base2.chksum_opt

    def test_reencode_same_obj(self):
        base = BaseVideo({"name": "test.mp4", "extension": "webm"}, {})
        reenc1 = base.reencode((100, 200))
        reenc2 = base.reencode((100, 200))
        assert len(base.reencodes.keys()) == 1
        assert reenc1 is reenc2

    def test_reencode_diff_resize(self):
        base = BaseVideo({"name": "test.mp4", "extension": "webm"}, {})
        base.reencode((100, 200))
        base.reencode((150, 300))
        assert len(base.reencodes.keys()) == 2
        reencs = list(base.reencodes.values())
        assert reencs[0] != reencs[1]

    def test_reencode_filepath(self):
        base = BaseVideo({"name": "test.mp4", "extension": "webm"}, {})
        reenc = base.reencode((100, 200))
        assert reenc == "test-%s-100x200.webm" % (
            crc32(bytes(json_dumps({"extension": "webm"}, sort_keys=True), "utf-8"))
        )

    def test_thumbnail_same_obj(self):
        base = BaseVideo({"name": "test.mp4"}, {})
        reenc1 = base.thumbnail((100, 200))
        reenc2 = base.thumbnail((100, 200))
        assert len(base.thumbnails.keys()) == 1
        assert reenc1 is reenc2

    def test_thumbnail_diff_resize(self):
        base = BaseVideo({"name": "test.mp4"}, {})
        base.thumbnail((100, 200))
        base.thumbnail((150, 300))
        assert len(base.thumbnails.keys()) == 2
        reencs = list(base.thumbnails.values())
        assert reencs[0] != reencs[1]

    def test_thumbnail_filepath(self):
        base = BaseVideo({"name": "test.mp4"}, {})
        reenc = base.thumbnail((100, 200))
        assert reenc == "test-%s-100x200.jpg" % (
            crc32(bytes(json_dumps({}, sort_keys=True), "utf-8"))
        )


# HACK because VideoFactory.base_vids does not seem to be reset between tests.
@pytest.fixture
def factory():
    yield
    VideoFactory.base_vids = dict()


@pytest.mark.usefixtures("factory")
# End HACK
class TestVideoFactory:
    def test_diff_paths_diff_videos(self):
        vid1 = VideoFactory.get("gallery1", {"name": "test1.mp4", "type": "video"})
        vid2 = VideoFactory.get("gallery2", {"name": "test2.mp4", "type": "video"})
        assert vid1 != vid2

    def test_same_path_diff_videos(self):
        vid1 = VideoFactory.get("gallery", {"name": "test1.mp4", "type": "video"})
        vid2 = VideoFactory.get("gallery", {"name": "test2.mp4", "type": "video"})
        assert vid1 != vid2

    def test_diff_paths_same_video(self):
        vid1 = VideoFactory.get("gallery1", {"name": "test.mp4", "type": "video"})
        vid2 = VideoFactory.get("gallery2", {"name": "test.mp4", "type": "video"})
        assert vid1 != vid2

    def test_same_path_same_video(self):
        vid1 = VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        vid2 = VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        assert vid1 is vid2

    def test_same_path_same_video_one_base_vids(self):
        VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        base_vids = VideoFactory.base_vids
        assert len(base_vids.keys()) == 1

    @pytest.mark.parametrize("gallery", ["gallery", "light/../gallery"])
    @pytest.mark.parametrize(
        "video",
        [
            {"name": "test.mp4", "type": "video"},
            {"name": "light/../test.mp4", "type": "video"},
        ],
    )
    def test_dotdot_paths(self, gallery, video):
        vid1 = VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        vid2 = VideoFactory.get(gallery, video)
        assert vid1 is vid2

    def test_base_vids_presence(self):
        vid1 = VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        base_vids = VideoFactory.base_vids
        assert len(base_vids.keys()) == 1
        assert vid1 is list(base_vids.values())[0]
