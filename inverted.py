#!/usr/bin/env python3
import argparse, csv, json, sys
from collections import defaultdict
from pathlib import Path

def build_inverted_index(tokens_tsv: Path) -> tuple[dict, int]:
    """
    Read a TSV with header: docno <tab> tokens
    'tokens' is a space-separated list of terms for that document (already cleaned in Part 2).
    Returns (inverted_index_dict, num_docs_seen).
    """
    postings = defaultdict(set)   # token -> set of docnos
    n_docs = 0

    with tokens_tsv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            docno = (row.get("docno") or "").strip()
            toks_str = row.get("tokens") or ""
            if not docno:
                continue
            n_docs += 1
            # de-duplicate per document to count DF correctly
            for tok in set(toks_str.split()):
                postings[tok].add(docno)

    # finalize: sets -> sorted lists, add df
    inverted = {tok: {"df": len(docs), "postings": sorted(docs)}
                for tok, docs in postings.items()}
    return inverted, n_docs

def main():
    ap = argparse.ArgumentParser(description="Part 3: Build inverted index from Part-2 tokens TSV")
    ap.add_argument("--input", required=True, help="Tokens TSV (header: docno\\ttokens)")
    ap.add_argument("--output", default="inverted_index.json", help="Output JSON path")
    ap.add_argument("--compact", action="store_true", help="Write compact JSON (no pretty indent)")
    args = ap.parse_args()

    inv, n_docs = build_inverted_index(Path(args.input))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as out:
        if args.compact:
            json.dump(inv, out, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(inv, out, ensure_ascii=False, indent=2)

    print(f"Docs indexed: {n_docs}   Unique tokens: {len(inv)}   Wrote: {out_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
