from cn_stock_mcp.providers.akshare_provider import AKShareProvider


class _Provider(AKShareProvider):
    pass


def test_call_ak_quietly_suppresses_stdout_and_stderr(capsys):
    provider = _Provider()

    def _noisy(a, b):
        print("stdout-noise")
        import sys

        print("stderr-noise", file=sys.stderr)
        return a + b

    result = provider._call_ak_quietly(_noisy, 1, 2)

    captured = capsys.readouterr()
    assert result == 3
    assert captured.out == ""
    assert captured.err == ""
