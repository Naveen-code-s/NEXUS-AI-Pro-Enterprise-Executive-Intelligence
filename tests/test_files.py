from utils.files import safe_name,checksum
def test_safe_name(): assert '/' not in safe_name('../a.pdf')
def test_checksum(): assert checksum(b'a')==checksum(b'a')
