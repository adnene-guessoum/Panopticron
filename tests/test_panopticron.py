"""test file for panopticron.py script"""
from dotenv import load_dotenv
from script import panopticron

load_dotenv()


class MockEmptyResponse:
    def json(self):
        return {}


class TestPanopticron:
    def test_panopticron(self, capsys):
        return_value = panopticron.main()
        capture = capsys.readouterr()
        assert capture.out == "TODO\n"
        assert capture.err == ""
        assert return_value == 0

    def test_sanity_check_user_activity_wrong_username(self, capsys, caplog):
        username = "nonexistentuser"
        response = MockEmptyResponse()  # github api response for nonexistent user
        sanity_check = panopticron.check_sanity_github_api_response(response, username)
        capture_out_err = capsys.readouterr()
        capture_log = caplog.text
        assert capture_out_err.out == ""
        assert capture_out_err.err == ""
        assert f"No data found for {username}" in capture_log
        assert sanity_check is None
