#ryan razzanos tokenizer
import argparse, csv, re, sys
from pathlib import Path

USE_APOSTROPHE_RULE = True
USE_STOPWORDS = True

STOPWORDS = None
def get_stopwords():
    global STOPWORDS
    if STOPWORDS is None:
        try:
            from nltk.corpus import stopwords
            STOPWORDS = set(stopwords.words("english"))
        except Exception:
            print("WARN: NLTK stopwords not available. Run: python -m nltk.downloader stopwords",
                  file=sys.stderr)
            STOPWORDS = set()
    return STOPWORDS

PUNCT_RE = re.compile(r"[\t\n\r.,;:!?(){}\[\]\"`~@#$%^&*+\-/=|<>_]")
APOS_RE = re.compile(r"['\u2019']")
SINGLE_APOS_SUFFIX_RE = re.compile(r"^(?P<stem>[A-Za-z0-9]+)'[A-Za-z]$")

def tokenize(text: str) -> list[str]:
    s = text.lower()
    s = PUNCT_RE.sub(" ", s)           
    s = " ".join(s.split())             
    return s.split() if s else []

def apostrophe_rule(tokens: list[str]) -> list[str]:
    if not USE_APOSTROPHE_RULE:
        
        return [APOS_RE.sub("", t) for t in tokens]
    out = []
    for t in tokens:
        m = SINGLE_APOS_SUFFIX_RE.match(t)
        out.append(m.group("stem") if m else APOS_RE.sub("", t))
    return out

def remove_stopwords(tokens: list[str]) -> list[str]:
    if not USE_STOPWORDS:
        return tokens
    sw = get_stopwords()
    return [t for t in tokens if t and t not in sw]

def process_text(text: str) -> list[str]:
    toks = tokenize(text)
    toks = apostrophe_rule(toks)
    toks = remove_stopwords(toks)
    return toks


def gather_text(row: dict, fields=("headline","byline","text")) -> str:
    parts = []
    for f in fields:
        v = row.get(f, "")
        if v: parts.append(v)
    return "\n".join(parts)

def main():
    ap = argparse.ArgumentParser(description="Part 2: Tokenization + Normalization over Part-1 TSV")
    ap.add_argument("--input", required=True, help="TSV from Part 1")
    ap.add_argument("--output", default="-", help="Output (docno + tokens) TSV (default stdout)")
    ap.add_argument("--fields", default="headline,byline,text",
                    help="Comma-separated fields to tokenize (default: headline,byline,text)")
    ap.add_argument("--no_stop", action="store_true", help="Unplug stopword removal")
    ap.add_argument("--no_apos_rule", action="store_true", help="Unplug apostrophe rule")
    args = ap.parse_args()

    global USE_STOPWORDS, USE_APOSTROPHE_RULE
    if args.no_stop: USE_STOPWORDS = False
    if args.no_apos_rule: USE_APOSTROPHE_RULE = False

    fields = [f.strip() for f in args.fields.split(",") if f.strip()]

    out = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8")
    try:
         
        print("docno\ttokens", file=out)
        with open(args.input, encoding="utf-8") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                docno = row.get("docno", "").strip()
                if not docno: continue
                text = gather_text(row, fields=fields)
                toks = process_text(text)
                print(f"{docno}\t{' '.join(toks)}", file=out)
    finally:
        if out is not sys.stdout:
            out.close()

if __name__ == "__main__":
    main()
