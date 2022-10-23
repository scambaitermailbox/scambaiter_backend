from .storer import store_addr, addr_exists, get_stored_info, scam_exists
from .gen import get_random_addr


def gen_new_addr(scam_email, sol_name):
    new_addr = get_random_addr()
    store_addr(new_addr, scam_email, sol_name)
    return new_addr
