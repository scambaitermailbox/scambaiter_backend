from typing import Optional

from secret import ADDR_SOL_PATH
import json
import os
import names
from collections import namedtuple

StoredInfo = namedtuple("StoredInfo", ["addr", "to", "sol", "username"])

if not os.path.exists(os.path.dirname(ADDR_SOL_PATH)):
    os.makedirs(os.path.dirname(ADDR_SOL_PATH))

if not os.path.exists(ADDR_SOL_PATH):
    with open(ADDR_SOL_PATH, "w", encoding="utf8") as f:
        json.dump({}, f)


def addr_exists(addr) -> bool:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    if addr in d:
        return True
    return False


def scam_exists(addr) -> bool:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    for bait in d:
        if d[bait]["to"] == addr:
            return True
    return False


def store_addr(addr, scam_email, sol_name):
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    d[addr] = {
        "to": scam_email,
        "sol": sol_name,
        "username": names.get_first_name()
    }

    with open(ADDR_SOL_PATH, "w", encoding="utf8") as f:
        json.dump(d, f, indent=4)


def get_stored_info(addr, scam_email) -> Optional[StoredInfo]:
    with open(ADDR_SOL_PATH, "r", encoding="utf8") as f:
        d = json.load(f)

    obj = None

    if addr not in d:
        for bait in d:
            if d[bait]["to"] == scam_email:
                obj = d[bait]
                addr = bait
                break
    else:
        obj = d[addr]
    if obj is None:
        return None
    return StoredInfo(addr, obj["to"], obj["sol"], obj["username"])
