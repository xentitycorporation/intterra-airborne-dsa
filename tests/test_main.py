from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from main import create_product_from_file_path, get_mission_details, get_product_s3_key
from models.product import Product


class TestMain(unittest.TestCase):
    def test_get_mission_details_success(self):
        now = datetime.now().replace(microsecond=0)
        with patch(
            "builtins.input",
            side_effect=["Buckwheat Ridge", now.strftime("%Y-%m-%d %H:%M")],
        ):
            mission_name, mission_time = get_mission_details()
            self.assertEqual(mission_name, "Buckwheat-Ridge")
            self.assertEqual(
                mission_time,
                now.astimezone(timezone.utc).replace(second=0).replace(tzinfo=None),
            )

    @patch("sys.exit")
    def test_get_mission_details_date_failure(self, mock_exit):
        with patch(
            "builtins.input",
            side_effect=["Buckwheat Ridge", "1"],
        ):
            get_mission_details()
            mock_exit.assert_called_once_with(1)

    @patch("os.path.getmtime", return_value=1234567890.0)
    def test_create_product_from_file_path_image(self, mock_getmtime):
        file_path = "images/EO/some_image.tif"
        expected_product = Product(
            "image", "EO", datetime.fromtimestamp(1234567890.0, tz=timezone.utc)
        )
        created_product = create_product_from_file_path(file_path)
        print(created_product)
        print(expected_product)
        self.assertEqual(created_product, expected_product)

        mock_getmtime.assert_called_once_with(file_path)

    @patch("os.path.getmtime", return_value=1234567890.0)
    def test_create_product_from_file_path_image_with_wrong_type_in_path(
        self, mock_getmtime
    ):
        file_path = "images/EO/IRimage.tif"
        expected_product = Product(
            "image", "EO", datetime.fromtimestamp(1234567890.0, tz=timezone.utc)
        )
        created_product = create_product_from_file_path(file_path)
        print(created_product)
        print(expected_product)
        self.assertEqual(created_product, expected_product)

        mock_getmtime.assert_called_once_with(file_path)

    @patch("os.path.getmtime", return_value=1234567890.0)
    def test_create_product_from_file_path_tactical(self, mock_getmtime):
        file_path = "tactical/Detection/some_detection.kml"
        expected_product = Product(
            "tactical",
            "Detection",
            datetime.fromtimestamp(1234567890.0, tz=timezone.utc),
        )
        created_product = create_product_from_file_path(file_path)
        self.assertEqual(created_product, expected_product)

        mock_getmtime.assert_called_once_with(file_path)

    @patch("os.path.getmtime", return_value=1234567890.0)
    def test_create_product_from_file_path_video(self, mock_getmtime):
        file_path = "videos/some_video.ts"
        expected_product = Product(
            "video", None, datetime.fromtimestamp(1234567890.0, tz=timezone.utc)
        )
        created_product = create_product_from_file_path(file_path)
        self.assertEqual(created_product, expected_product)

        mock_getmtime.assert_called_once_with(file_path)

    @patch("os.path.getmtime", return_value=1234567890.0)
    def test_create_product_from_file_path_invalid(self, mock_getmtime):
        file_path = "invalid_path/some_file.txt"
        with self.assertRaises(ValueError):
            create_product_from_file_path(file_path)

        mock_getmtime.assert_called_once_with(file_path)

    def test_get_product_s3_key_image_eo(self):
        product = Product("image", "EO", datetime.now(timezone.utc))
        s3_key = get_product_s3_key("Mission123", product, ".tif")
        expected_s3_key = f"IMAGERY/{product.timestamp.strftime('%Y%m%d_%H%M%SZ')}_Mission123_EOimage.tif"
        self.assertEqual(s3_key, expected_s3_key)

    def test_get_product_s3_key_tactical_detection(self):
        product = Product("tactical", "Detection", datetime.now(timezone.utc))
        s3_key = get_product_s3_key("Mission456", product, ".kml")
        expected_s3_key = f"TACTICAL/{product.timestamp.strftime('%Y%m%d_%H%M%SZ')}_Mission456_Detection.kml"
        self.assertEqual(s3_key, expected_s3_key)

    def test_get_product_s3_key_video(self):
        product = Product("video", None, datetime.now(timezone.utc))
        s3_key = get_product_s3_key("Mission789", product, ".ts")
        expected_s3_key = (
            f"VIDEO/{product.timestamp.strftime('%Y%m%d_%H%M%SZ')}_Mission789_Video.ts"
        )
        self.assertEqual(s3_key, expected_s3_key)
