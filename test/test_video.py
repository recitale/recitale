import pytest

from pathlib import Path
from unittest.mock import patch

from recitale.video import BaseVideo, VideoFactory


class TestVideoCommon:
    check_output = '{ "streams": [{ "height": 480, "width": 840}] }'

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
        assert vid1 == vid2

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
        assert vid1 == vid2

    def test_base_vids_presence(self):
        vid1 = VideoFactory.get("gallery", {"name": "test.mp4", "type": "video"})
        base_vids = VideoFactory.base_vids
        assert len(base_vids.keys()) == 1
        assert vid1 == list(base_vids.values())[0]
