from src import emailer
def test_emailer_import():
    assert hasattr(emailer, 'send_email')
