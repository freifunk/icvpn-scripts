from . import mkbgp

def test_bird_formatter_shows_interface_for_link_local():
    bfmd = mkbgp.BirdFormatter()
    bfmd.add_data("4711", "Das Test-AS", "template", "fe80::42", "eth42")
    assert 'fe80::42%eth42 as 4711' in bfmd.finalize()

def test_bird_formatter_shows_interface_for_non_link_local():
    bfmd = mkbgp.BirdFormatter()
    bfmd.add_data("4711", "Das Test-AS", "template", "2001::42", "eth42")
    assert '2001::42 as 4711' in bfmd.finalize()


def test_quagga_formatter_shows_interface_for_link_local():
    qfmd = mkbgp.QuaggaFormatter()
    qfmd.add_data("4711", "Das Test-AS", "template", "fe80::42", "eth42")
    result = qfmd.finalize()
    assert "neighbor fe80::42%eth42 remote-as 4711" in result
    assert "neighbor fe80::42%eth42 description Das Test-AS" in result
    assert "neighbor fe80::42%eth42 peer-group template" in result

def test_quagga_formatter_shows_interface_for_non_link_local():
    qfmd = mkbgp.QuaggaFormatter()
    qfmd.add_data("4711", "Das Test-AS", "template", "2001::42", "eth42")
    result = qfmd.finalize()
    assert "neighbor 2001::42 remote-as 4711" in result
    assert "neighbor 2001::42 description Das Test-AS" in result
    assert "neighbor 2001::42 peer-group template" in result
 