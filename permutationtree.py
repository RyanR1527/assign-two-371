import argparse
import json
from pathlib import Path
import bisect

def gen_permuterms(term: str) -> list[str]:
    w = term + "$"
    return [w[i:] + w[:i] for i in range(len(w))]

def build_perm_map(terms: list[str]) -> dict[str, str]:
    perm_map = {}
    for term in terms:
        for perm in gen_permuterms(term):
            perm_map[perm] = term
    return perm_map

def wildcard_to_prefix(query: str) -> str:
    if query.count("*") != 1:
        raise ValueError("Only one '*' wildcard is supported.")
    pre, suf = query.split("*", 1)
    return f"{suf}${pre}"

def search_permuterms(query: str, permuterm_dict: dict) -> list[str]:
    prefix = wildcard_to_prefix(query)
    permuterms = sorted(permuterm_dict.keys())
    idx = bisect.bisect_left(permuterms, prefix)
    results = []
    while idx < len(permuterms) and permuterms[idx].startswith(prefix):
        results.append(permuterm_dict[permuterms[idx]])
        idx += 1
    print(f"Found {len(results)} matching terms")
    return results

def main():
    ap = argparse.ArgumentParser(description="Permuterm index with wildcard search")
    ap.add_argument("--inverted", required=True, help="Inverted index JSON from Part 3")
    ap.add_argument("--query", help="Wildcard query with exactly one * (e.g., pre*suf, S*, *S)")
    ap.add_argument("--name", default="YourName", help="Name for TREC output column 6")
    ap.add_argument("--rankval", default="0", help="Column 4 (rank). Spec says 0 for Boolean.")
    args = ap.parse_args()

    inv = json.load(open(args.inverted, encoding="utf-8"))
    vocab = sorted(inv.keys())
    perm_map = build_perm_map(vocab)

    if args.query:
        terms = search_permuterms(args.query, perm_map)
        for term in terms:
            doc_ids = inv.get(term, {}).get("postings", [])
            for doc_id in doc_ids:
                print(f"0 1 {doc_id} {args.rankval} 1.0 {args.name}")

if __name__ == "__main__":
    main()
