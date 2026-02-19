import re

# named capture groups
pat = re.compile(
    r"(?m)^(?P<top>\d+\t[^\r\n]*)\r?\n"
    r"(?P<header>\*[^\r\n]*)\r?\n"
    r"(?P<content>(?:\t[^\r\n]*\r?\n)+)"
    r"(?=0\r?\n\*\r?\n)"
)

m = pat.search(text)  # first block
# or: for m in pat.finditer(text):  # all blocks

top = m.group("top")
header = m.group("header")
content = m.group("content")  # contains all tabbed lines (with newlines)
lines = content.splitlines()  # list of content lines (tabs preserved)

# If you want content lines without the leading tab (still no “re-filtering”, just a clean transform):
content_lines = [ln[1:] for ln in m.group("content").splitlines()]


blocks = [
    (m.group("top"), m.group("header"), m.group("content")) for m in pat.finditer(text)
]

blocks = [
    (m.group("top"), m.group("header"), m.group("content")) for m in pat.finditer(text)
]

# 1) Regex for the file preamble
import re

preamble_re = re.compile(
    r"(?m)\A(?P<fileline>\d+\s+[^\r\n]+)\r?\n" r"(?P<comments>(?:\*[^\r\n]*\r?\n)*)"
)

# 2) Regex for each block
block_re = re.compile(
    r"(?m)^(?P<top>\d+\t[^\r\n]*)\r?\n"
    r"(?P<header>\*[^\r\n]*)\r?\n"
    r"(?P<content>(?:\t[^\r\n]*\r?\n)+)"
    r"(?=0\r?\n\*\r?\n)"
)

# Parsing the whole file (no refiltering needed)
text = open("yourfile.txt", "r", encoding="utf-8").read()

pm = preamble_re.search(text)
fileline = pm.group("fileline") if pm else None
comments = pm.group("comments") if pm else ""

start = pm.end() if pm else 0

blocks = []
for m in block_re.finditer(text, start):
    blocks.append(
        {
            "top": m.group("top"),
            "header": m.group("header"),
            "content": m.group("content"),  # big multiline string
            "content_lines": m.group("content").splitlines(),  # list of lines
        }
    )

print(fileline)
print(len(blocks))

# If you want to strip the leading tab from each content line
for b in blocks:
    b["content_lines_no_tab"] = [ln[1:] for ln in b["content_lines"]]
