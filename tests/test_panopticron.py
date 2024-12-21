"""test file for panopticron.py script"""
import os

from dotenv import load_dotenv
from script import panopticron

load_dotenv()

# use the following to test with own GitHub username
PERSONAL_GITHUB_USERNAME = os.getenv("PERSONAL_GITHUB_USERNAME")


class TestPanopticron:
    def test_panopticron(self, capsys):
        return_value = panopticron.main()
        capture = capsys.readouterr()
        assert capture.out == "TODO\n"
        assert capture.err == ""
        assert return_value == 0

    def test_working_get_user_activity(self):
        response = panopticron.get_user_activity(PERSONAL_GITHUB_USERNAME)
        assert response is not None
        assert isinstance(response, list)

    def test_get_user_activity_wrong_username(self, capsys, caplog):
        username = "nonexistentuser"
        response = panopticron.get_user_activity(username)
        capture_out_err = capsys.readouterr()
        capture_log = caplog.text
        assert capture_out_err.out == ""
        assert capture_out_err.err == ""
        assert f"No data found for {username}" in capture_log
        assert response is None
