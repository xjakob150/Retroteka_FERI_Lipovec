import pytest

from pricing import services
from pricing.ebay import EbayError


class FakeEbay:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result, error, []

    def price_for(self, item):
        self.calls.append(item)
        if self.error:
            raise self.error
        return self.result


@pytest.fixture(autouse=True)
def ebay(monkeypatch):
    """Testi nikoli ne kličejo pravega eBaya; privzeto je eBay nedosegljiv, test pa lahko nastavi odgovor."""
    def use(**kwargs):
        fake = FakeEbay(**kwargs)
        monkeypatch.setattr(services, 'get_client', lambda: fake)
        return fake

    use(error=EbayError('eBay is not called in tests'))
    return use
