import json
import os
import pytest

from unittest.mock import call, mock_open, patch

from recitale.cache import Cache, CACHE_VERSION
from recitale.utils import remove_superficial_options


@pytest.fixture
def cache():
    return Cache(json=json)


class TestCache:
    def test_new_cache(self, cache):
        assert dict(cache.cache) == {"version": CACHE_VERSION}

    @patch("recitale.cache.os.path.exists", return_value=True)
    def test_load_cache(self, mock_ospath):
        cache_json = {"version": CACHE_VERSION, "some": "value"}
        with patch("builtins.open", mock_open(read_data=json.dumps(cache_json))):
            cache = Cache(json=json)

        assert dict(cache.cache) == cache_json

    @patch("recitale.cache.os.path.exists", return_value=True)
    @pytest.mark.parametrize(
        "cache_dict", [{"version": CACHE_VERSION + 1}, {"some": "value"}]
    )
    def test_load_old_cache(self, mock_ospath, cache_dict):
        with patch("builtins.open", mock_open(read_data=json.dumps(cache_dict))):
            cache = Cache(json=json)

        assert dict(cache.cache) == {"version": CACHE_VERSION}

    def test_dump_cache(self, cache):
        with patch("builtins.open", mock_open()) as p:
            cache.cache_dump()

        p.assert_called_with(os.path.join(os.getcwd(), ".recitale_cache"), "w")
        p.return_value.write.assert_has_calls(
            [
                call("{"),
                call('"version"'),
                call(": "),
                call(str(CACHE_VERSION)),
                call("}"),
            ]
        )

    @patch(
        "recitale.cache.remove_superficial_options", return_value={"some": "options"}
    )
    @patch("recitale.cache.os.path.getsize", return_value=12345678)
    def test_cache_picture(self, mock_ossize, mock_options, cache):
        cache.cache_picture("some.jpg", "thumbnail/path/some.jpg", {"some": "options"})
        assert cache.cache["thumbnail/path/some.jpg"] == {
            "size": 12345678,
            "options": {"some": "options"},
        }
        mock_options.assert_called_once_with({"some": "options"})

    def test_needs_to_be_generated_target_not_found(self, cache):
        ret = cache.needs_to_be_generated("source.jpg", "/notfound/target.jpg", {})
        assert ret is True

    @patch("recitale.cache.os.path.exists", return_value=True)
    def test_needs_to_be_generated_not_in_cache(self, mock_json, cache):
        ret = cache.needs_to_be_generated("source.jpg", "target.jpg", {})

        assert ret is True

    @patch("recitale.cache.os.path.exists", return_value=True)
    @patch("recitale.cache.os.path.getsize", return_value=12345678)
    def test_needs_to_be_generated_diff_size(self, mock_ossize, mock_ospath, cache):
        with patch.dict(
            cache.cache,
            {
                "/path/target.jpg": {
                    "size": 87654321,
                }
            },
        ):
            ret = cache.needs_to_be_generated("source.jpg", "/path/target.jpg", {})
        assert ret is True
        mock_ospath.assert_called_once()
        mock_ossize.assert_called_once_with("source.jpg")

    @patch(
        "recitale.cache.remove_superficial_options",
        side_effect=remove_superficial_options,
    )
    @patch("recitale.cache.os.path.exists", return_value=True)
    @patch("recitale.cache.os.path.getsize", return_value=12345678)
    def test_needs_to_be_generated_diff_options(
        self, mock_ossize, mock_ospath, mock_options, cache
    ):
        with patch.dict(
            cache.cache, {"/path/target.jpg": {"size": 12345678, "options": {}}}
        ):
            ret = cache.needs_to_be_generated(
                "source.jpg", "/path/target.jpg", {"some": "option"}
            )

        assert ret is True
        mock_ospath.assert_called_once()
        mock_ossize.assert_called_once_with("source.jpg")
        mock_options.assert_called_once_with({"some": "option"})

    @patch(
        "recitale.cache.remove_superficial_options",
        side_effect=remove_superficial_options,
    )
    @patch("recitale.cache.os.path.exists", return_value=True)
    @patch("recitale.cache.os.path.getsize", return_value=12345678)
    def test_needs_to_be_generated_same(
        self, mock_ossize, mock_ospath, mock_options, cache
    ):
        options = {"option": 1}
        with patch.dict(
            cache.cache, {"/path/target.jpg": {"size": 12345678, "options": options}}
        ):
            ret = cache.needs_to_be_generated("source.jpg", "/path/target.jpg", options)

        assert ret is False
        mock_ospath.assert_called_once()
        mock_ossize.assert_called_once_with("source.jpg")
        mock_options.assert_called_once_with(options)

    @patch(
        "recitale.cache.remove_superficial_options",
        side_effect=remove_superficial_options,
    )
    @patch("recitale.cache.os.path.exists", return_value=True)
    @patch("recitale.cache.os.path.getsize", return_value=12345678)
    def test_needs_to_be_generated_options_tuple(
        self, mock_ossize, mock_ospath, mock_options, cache
    ):
        options = {"option": (0, 1)}
        with patch.dict(
            cache.cache,
            json.loads(
                json.dumps({"/path/target.jpg": {"size": 12345678, "options": options}})
            ),
        ):
            ret = cache.needs_to_be_generated("source.jpg", "/path/target.jpg", options)

        assert ret is False
        mock_ospath.assert_called_once()
        mock_ossize.assert_called_once_with("source.jpg")
        mock_options.assert_called_once_with(options)
