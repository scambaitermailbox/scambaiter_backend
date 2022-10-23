import re

import enchant
from enchant.checker import SpellChecker

NEWLINE_PATTERN = re.compile("<br>|\n")
dictionary = enchant.Dict("en_US")


class RawTextFilter:
    def filter(self, raw: str):
        raw = raw.strip()
        return raw.replace("\r\n", "\n")


class RemoveNewlineTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveNewlineTextFilter, self).filter(raw)
        raw = re.sub("[\r\n]+", " ", raw)
        return raw


class CombineNewlineTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(CombineNewlineTextFilter, self).filter(raw)
        raw = re.sub("[\r\n]+", "\n", raw)
        return raw


class ReplaceNewlineTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(ReplaceNewlineTextFilter, self).filter(raw)
        raw = re.sub(r"( *[\r\n] *)+", "<br>", raw)
        raw = re.sub(r"\s*?(<br>\s*)+", "<br>", raw)
        return raw


class EnronLineCombinationTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(EnronLineCombinationTextFilter, self).filter(raw)
        raw = re.sub(r"=.*(\b|\n|\r\n)", "", raw)
        return raw


class RemoveOpeningEndingTextFilter(ReplaceNewlineTextFilter):
    MINIMUM_WORDS = 7

    def filter(self, raw: str):
        raw = super(RemoveOpeningEndingTextFilter, self).filter(raw)
        lines = raw.split("<br>")
        start = 0

        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("__label__"):
                start = i
                break

            if line.lower().startswith("dear"):
                continue

            if ":" in line:
                continue
            try:
                if not dictionary.check(line.split(" ")[0]):
                    continue
            except ValueError:
                continue

            if len(line.split(" ")) > self.MINIMUM_WORDS:
                start = i
                break

        end = start + 1
        for i in range(len(lines) - 1, start, -1):
            line = lines[i].strip()

            line_lower = line.lower()
            if line_lower.startswith("yours") or line_lower.startswith("best") or line_lower.startswith("kind"):
                continue

            if len(line.split(" ")) > self.MINIMUM_WORDS:
                end = i + 1
                break

        return "\n".join(lines[start:end])


class RemoveSensitiveInfoTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveSensitiveInfoTextFilter, self).filter(raw)

        # href
        raw = re.sub(r"<[aA].*>", " ", raw, flags=re.DOTALL)

        # Url
        raw = re.sub(r"[a-zA-z]+://[^\s]*", " ", raw)
        raw = re.sub(r"(\w+\.){2,}\w+", " ", raw)

        # Date & Time
        raw = re.sub(r"\d+[:/\\]\d+([:/\\]\d+)?", " ", raw)
        raw = re.sub(r" [AP]M", " ", raw, flags=re.IGNORECASE)

        # Tel
        raw = re.sub(r"[\d\- ]{5,}", " ", raw)

        # Email
        raw = re.sub(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", " ", raw)

        # Time
        raw = re.sub(r"([0-1]?[0-9]|[2][0-3]):([0-5][0-9])", " ", raw)
        raw = re.sub(r" [APap]\.?[mM]\.? ", "", raw)

        return raw


class RemovePunctuationTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemovePunctuationTextFilter, self).filter(raw)
        return re.sub(r"[^a-zA-Z0-9\-\n]+", " ", raw)


class RemoveSpecialPunctuationTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveSpecialPunctuationTextFilter, self).filter(raw)
        return re.sub(r"[^a-zA-Z0-9\-\n,.?'_\[\]]", " ", raw)


class RemoveSymbolLineTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveSymbolLineTextFilter, self).filter(raw)
        symbol_p = re.compile("^[^a-zA-Z0-9]{5,}")

        res = []
        for line in re.split(NEWLINE_PATTERN, raw):
            if not (line.startswith(">") or symbol_p.match(line)):
                res.append(line)

        return "\n".join(res)


class RemoveEnronHeaderTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveEnronHeaderTextFilter, self).filter(raw)

        res = []
        found = False
        for line in re.split(NEWLINE_PATTERN, raw):
            if line.startswith("X-FileName: "):
                found = True
                continue

            if found:
                res.append(line)

        return "\n".join(res)


class RemoveInfoLineTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveInfoLineTextFilter, self).filter(raw)

        # For multi To: line
        raw = re.sub(r"to:.*?\n(?=cc)", "", raw, flags=re.DOTALL | re.IGNORECASE)

        res = []
        # p = re.compile(".*(From|Sent|To|Cc|Subject|Importance):.*", flags=re.IGNORECASE)
        p = re.compile(r"^[a-zA-Z -]+:.*$")

        for line in re.split(NEWLINE_PATTERN, raw):
            if not p.match(line):
                res.append(line)

        return "\n".join(res)


class RemoveEnronFileTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveEnronFileTextFilter, self).filter(raw)
        raw = re.sub(r"<< *File: .*>>", " ", raw, flags=re.IGNORECASE)
        return raw


class MultiSymbolIntegrationTextFilter(RawTextFilter):
    def filter(self, raw: str):
        raw = super(MultiSymbolIntegrationTextFilter, self).filter(raw)
        raw = re.sub(r" +", " ", raw)
        raw = re.sub(r"(<br>)+", "<br>", raw)
        raw = re.sub(r"\n+", "\n", raw)
        raw = re.sub(r"([,.])[,. ]+", r"\1 ", raw)
        raw = re.sub(r" \n", "\n", raw)
        return raw


class RemoveStrangeWord(RawTextFilter):
    def filter(self, raw: str):
        raw = super(RemoveStrangeWord, self).filter(raw)

        res = ""

        for line in raw.splitlines():
            for word in line.split(" "):
                if len(word) < 2:
                    continue

                if len(word) > 10 and not ("_" in word):
                    continue

                if any(l.isalpha() for l in word) and any(l.isnumeric() for l in word):
                    continue

                if not re.match(r"^\[?(([A-Z'_][a-z'_]+)|([A-Z'_]+)|([a-z'_]+))[,.'?]*]?$", word):
                    continue

                res += word + " "
            res += "\n"

        return res
