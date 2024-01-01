"""Unit tests for image retriever."""
import logging
import pytest
import os

from common.image_retriever import ImageRetriever
from common.display_config import DisplayConfig


TEST_IMAGE_DIR = "./test-images"


@pytest.fixture()
def image_retriever():
    """TODO"""
    display_config = DisplayConfig(
        logging.getLogger(), './tests/test_display_config.json')
    yield ImageRetriever(logging.getLogger(), display_config)


class TestImageRetriever:
    """Unit test suite for the image retriever."""

    def test_image_extension_filtering(self):
        """TODO"""
        # TODO
        pass

    def test_get_all_image_paths(self, image_retriever):
        """TODO"""

        actual_images = set(image_retriever.get_path_of_all_images())

        all_files = os.listdir(TEST_IMAGE_DIR)
        expected_images = set(
            [f"{TEST_IMAGE_DIR}/{f}" for f in all_files if not os.path.isdir(f)])

        assert actual_images == expected_images

    def test_get_random_image():
        """TODO"""

    def test_get_random_images():
        """TODO"""
