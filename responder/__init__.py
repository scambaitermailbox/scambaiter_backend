import json
import os
from collections import namedtuple, defaultdict

from secret import MODEL_HISTORY_PATH
from .replier import SimpleReplier, NeoEnronReplier, NeoRawReplier, Replier, ClassifierReplier, TemplateReplier

#replier_list = [ClassifierReplier(), NeoEnronReplier(), NeoRawReplier()]

replier_list = [SimpleReplier()]


ReplyResult = namedtuple("ReplyResult", ["name", "text"])

if not os.path.exists(os.path.dirname(MODEL_HISTORY_PATH)):
    os.makedirs(os.path.dirname(MODEL_HISTORY_PATH))

if not os.path.exists(MODEL_HISTORY_PATH):
    d = {}
    for r in replier_list:
        d[r.name] = 0
    with open(MODEL_HISTORY_PATH, "w", encoding="utf8") as f:
        json.dump(d, f)


def get_replier_by_name(name):
    for r in replier_list:
        if r.name == name:
            return r
    return None


def get_replier_randomly() -> Replier:
    with open(MODEL_HISTORY_PATH, "r", encoding="utf8") as f:
        j = json.load(f)

    count_dict = defaultdict(int, j)
    res = min(count_dict, key=count_dict.get)
    count_dict[res] += 1
    with open(MODEL_HISTORY_PATH, "w", encoding="utf8") as f:
        json.dump(count_dict, f)

    return get_replier_by_name(res)


def get_reply_random(mail_body) -> ReplyResult:
    r = get_replier_randomly()
    text = r.get_reply(mail_body)
    res = ReplyResult(r.name, text)
    return res


def get_reply_with_solution(mail_body, name) -> str:
    r = get_replier_by_name(name)
    if r is not None:
        return r.get_reply(mail_body)
    else:
        return "SOLUTION_NOT_FOUND"
