import random
import string

from .storer import addr_exists
from secret import DOMAIN_NAME


def get_random_addr():
    while True:
        res = ""
        for i in range(2):
            res += random.choice(string.ascii_lowercase)

        for i in range(5):
            res += random.choice(string.digits)

        if not addr_exists(res):
            return res + "@" + DOMAIN_NAME
