import brainflex


class TestVersion:
    def test_version(self):
        assert isinstance(brainflex.__version__, str)
