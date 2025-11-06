
#requires downloading beautifulsoap from terminal to run (Assuming this is being viewed from vscode)
#Ryan Rs assignment one



import argparse, sys
from pathlib import Path
from bs4 import BeautifulSoup

FIELDS = ["docno","profile","date","headline","byline","text","pub","page","cn","in","tp"]

def files(p: Path):
    if p.is_file(): yield p
    else:
        for f in sorted(p.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                yield f

def txt(el, tag):
    node = el.find(tag)
    return node.get_text(" ", strip=True) if node else ""

def lst(el, tag):
    node = el.find(tag)
    if not node: return ""
    items = []
    for line in node.get_text("\n", strip=True).split("\n"):
        for piece in line.split(";"):
            s = " ".join(piece.split()).strip(" .,:")
            if s: items.append(s)
    return "; ".join(items)

def parse_doc(block_html):
    s = BeautifulSoup(block_html, "html.parser")
    d = {
        "docno": txt(s,"docno"),
        "profile": txt(s,"profile"),
        "date": txt(s,"date"),
        "headline": txt(s,"headline"),
        "byline": txt(s,"byline"),
        "text": txt(s,"text"),
        "pub": txt(s,"pub"),
        "page": txt(s,"page"),
        "cn": lst(s,"cn"),
        "in": lst(s,"in"),
        "tp": lst(s,"tp"),
    }
    return d if d["docno"] else None

def parse_file(fp: Path):
    try:
        raw = fp.read_text(encoding="latin-1")
    except Exception:
        raw = fp.read_text(encoding="utf-8", errors="ignore")
    for chunk in raw.split("</DOC>"):
        if "<DOC" not in chunk: continue
        block = "<DOC" + chunk.split("<DOC",1)[-1] + "</DOC>"
        rec = parse_doc(block)
        if rec: yield rec

def main():
    ap = argparse.ArgumentParser(description="Part 1: Parse FT (TREC) → TSV")
    ap.add_argument("--input", required=True, help="FT file or directory")
    ap.add_argument("--output", default="-", help="TSV output (default stdout)")
    args = ap.parse_args()

    out = sys.stdout if args.output == "-" else open(args.output,"w",encoding="utf-8")
    print("\t".join(FIELDS), file=out)
    n_docs = 0
    for f in files(Path(args.input)):
        for rec in parse_file(f):
            row = [ (rec.get(k,"") or "").replace("\t"," ").replace("\n"," ").strip() for k in FIELDS ]
            print("\t".join(row), file=out)
            n_docs += 1
    if out is not sys.stdout: out.close()
    print(f"Documents: {n_docs}", file=sys.stderr)

if __name__ == "__main__":
    main()
