from . import scamletterinfo
from . import scamsurvivors


def fetch_all():
    scamletterinfo.fetch()
    scamsurvivors.fetch()
