from datetime import datetime
import unittest
from unittest.mock import patch

from airborne_dsa.main import get_mission_details


class TestMain(unittest.TestCase):
    def test_get_mission_details_success(self):
        now = datetime.now().replace(microsecond=0)
        with patch(
            "builtins.input",
            side_effect=["Buckwheat Ridge", now.strftime("%Y-%m-%d_%H:%M:%S")],
        ):
            mission_name, mission_time = get_mission_details()
            self.assertEqual(mission_name, "BuckwheatRidge")
            self.assertEqual(mission_time, now)

    @patch("sys.exit")
    def test_get_mission_details_date_failure(self, mock_exit):
        with patch(
            "builtins.input",
            side_effect=["Buckwheat Ridge", "1"],
        ):
            get_mission_details()
            mock_exit.assert_called_once_with(1)
