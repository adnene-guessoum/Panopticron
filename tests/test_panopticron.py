"""test file for panopticron.py script"""
import datetime

from script import panopticron

TARGET_GITHUB_USERNAME = "testuser"


class MockEmptyResponse:
    def json(self):
        return {}


class ValidUserActivity:
    """mock response for user activity to keep."""

    @staticmethod
    def get_user_activity():
        now = datetime.datetime.now(datetime.timezone.utc)
        return [
            {
                "created_at": (now - datetime.timedelta(hours=1)).isoformat(),
                "type": "PushEvent",
                "repo": {"name": "testuser/test-repo"},
                "url": "https://api.github.com/events/123456789",
            },
            {
                "created_at": (now - datetime.timedelta(hours=3)).isoformat(),
                "type": "PullRequestEvent",
                "repo": {"name": "testuser/another-repo"},
                "url": "https://api.github.com/events/987654321",
            },
        ]


class InvalidUserActivity:
    """mock response for user activity from 2 days ago."""

    @staticmethod
    def get_user_activity():
        now = datetime.datetime.now(datetime.timezone.utc)
        return [
            {
                "created_at": (now - datetime.timedelta(days=2)).isoformat(),
                "type": "IssueCommentEvent",
                "repo": {"name": "testuser/old-repo"},
                "url": "https://api.github.com/events/111111111",
            }
        ]


class TestPanopticron:
    def test_main_wrong_target_username(self, caplog):
        panopticron.main(TARGET_GITHUB_USERNAME)
        capture_log = caplog.text
        assert f"No data found for {TARGET_GITHUB_USERNAME}" in capture_log
        assert "No email will be sent. Exiting script..." in capture_log
        assert "Check if the username is correct. testuser" in capture_log

    def test_check_sanity_github_api_response_wrong_username(self, capsys, caplog):
        response = MockEmptyResponse()  # github api response for nonexistent user
        sanity_check = panopticron.check_sanity_github_api_response(
            response, TARGET_GITHUB_USERNAME
        )
        capture_out_err = capsys.readouterr()
        capture_log = caplog.text
        assert capture_out_err.out == ""
        assert capture_out_err.err == ""
        assert f"No data found for {TARGET_GITHUB_USERNAME}" in capture_log
        assert "No email will be sent. Exiting script..." in capture_log
        assert (
            f"Check if the username is correct. {TARGET_GITHUB_USERNAME}" in capture_log
        )
        assert sanity_check is None

    def test_filter_last_24_hours_activity_valid(self):
        user_activity = ValidUserActivity.get_user_activity()
        result = panopticron.filter_last_24_hours_activity(user_activity)
        assert len(result) == 2
        assert "PushEvent" in result[0]
        assert "PullRequestEvent" in result[1]

    def test_filter_last_24_hours_activity_invalid(self):
        user_activity = InvalidUserActivity.get_user_activity()
        result = panopticron.filter_last_24_hours_activity(user_activity)
        assert len(result) == 0
