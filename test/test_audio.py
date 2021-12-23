import pytest

from unittest.mock import patch

from recitale.audio import AudioFactory, BaseAudio


class TestAudioCommon:
    check_output = '{ "format": {"duration": "10.4"} }'

    def test_duration_base(self):
        AudioFactory.global_options = {"binary": "ffmpeg", "extension": "mp3"}
        baud = BaseAudio({"name": "test.mp3"}, AudioFactory.global_options)
        with patch(
            "recitale.audio.subprocess.check_output", return_value=self.check_output
        ):
            assert baud.duration == 10.4

    def test_duration_base_only_one_subprocess(self):
        AudioFactory.global_options = {"binary": "ffmpeg", "extension": "mp3"}
        baud = BaseAudio({"name": "test.mp3"}, AudioFactory.global_options)
        with patch(
            "recitale.audio.subprocess.check_output", return_value=self.check_output
        ):
            assert baud.duration == 10.4
        assert baud.duration == 10.4


# HACK because AudioFactory.base_audios does not seem to be reset between tests.
@pytest.fixture
def factory():
    yield
    AudioFactory.base_audios = dict()


@pytest.mark.usefixtures("factory")
# End HACK
class TestAudioFactory:
    def test_diff_paths_diff_audios(self):
        audio1 = AudioFactory.get("gallery1", "test1.mp3")
        audio2 = AudioFactory.get("gallery2", "test2.mp3")
        assert audio1 != audio2

    def test_same_path_diff_audios(self):
        audio1 = AudioFactory.get("gallery", "test1.mp3")
        audio2 = AudioFactory.get("gallery", "test2.mp3")
        assert audio1 != audio2

    def test_diff_paths_same_audio(self):
        audio1 = AudioFactory.get("gallery1", "test.mp3")
        audio2 = AudioFactory.get("gallery2", "test.mp3")
        assert audio1 != audio2

    def test_same_path_same_audio(self):
        audio1 = AudioFactory.get("gallery", "test.mp3")
        audio2 = AudioFactory.get("gallery", "test.mp3")
        assert audio1 == audio2

    def test_same_path_same_audio_one_base_audios(self):
        AudioFactory.get("gallery", "test.mp3")
        AudioFactory.get("gallery", "test.mp3")
        base_audios = AudioFactory.base_audios
        assert len(base_audios.keys()) == 1

    @pytest.mark.parametrize("gallery", ["gallery", "light/../gallery"])
    @pytest.mark.parametrize("audio", ["test.mp3", "light/../test.mp3"])
    def test_dotdot_paths(self, gallery, audio):
        audio1 = AudioFactory.get("gallery", "test.mp3")
        audio2 = AudioFactory.get(gallery, audio)
        assert audio1 == audio2

    def test_base_audios_presence(self):
        audio1 = AudioFactory.get("gallery", "test.mp3")
        base_audios = AudioFactory.base_audios
        assert len(base_audios.keys()) == 1
        assert audio1 == list(base_audios.values())[0]
