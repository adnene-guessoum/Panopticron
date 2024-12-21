"""test file for panopticron.py script"""
from script import panopticron


class TestPanopticron:
    def test_panopticron(self, capsys):
        return_value = panopticron.main()
        capture = capsys.readouterr()
        assert capture.out == "TODO\n"
        assert capture.err == ""
        assert return_value == 0
