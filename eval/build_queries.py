import json
from pathlib import Path

METADATA = Path("vector_store/metadata.json")

with open(METADATA, encoding="utf8") as f:
    metadata = json.load(f)

symbols = {}

for chunk in metadata:

    md = chunk["metadata"]

    file = Path(md["file"]).name

    symbols[md["name"]] = {
        "file": file,
        "name": md["name"],
        "start_line": md["start_line"],
    }

QUERIES = [

    ("R01","Where is HTTPAdapter defined?","HTTPAdapter"),
    ("R02","Where is HTTPAdapter.__init__ defined?","HTTPAdapter.__init__"),
    ("R03","Where is init_poolmanager defined?","HTTPAdapter.init_poolmanager"),
    ("R04","Where is proxy_manager_for defined?","HTTPAdapter.proxy_manager_for"),
    ("R05","Where is cert_verify defined?","HTTPAdapter.cert_verify"),

    ("R06","Where is Session defined?","Session"),
    ("R07","Where is Session.send defined?","Session.send"),
    ("R08","Where is resolve_redirects defined?","SessionRedirectMixin.resolve_redirects"),
    ("R09","Where is rebuild_proxies defined?","SessionRedirectMixin.rebuild_proxies"),
    ("R10","Where is rebuild_auth defined?","SessionRedirectMixin.rebuild_auth"),

    ("R11","Where is PreparedRequest defined?","PreparedRequest"),
    ("R12","Where is prepare_url defined?","PreparedRequest.prepare_url"),
    ("R13","Where is prepare_headers defined?","PreparedRequest.prepare_headers"),

    ("R14","Where is Response defined?","Response"),

    ("R15","Where is HTTPDigestAuth defined?","HTTPDigestAuth"),

    ("R16","How does Requests initialize its connection pool?","HTTPAdapter.init_poolmanager"),
    ("R17","How are redirects handled?","SessionRedirectMixin.resolve_redirects"),
    ("R18","How does Requests verify SSL certificates?","HTTPAdapter.cert_verify"),
    ("R19","How are request URLs prepared?","PreparedRequest.prepare_url"),
    ("R20","How is Digest authentication implemented?","HTTPDigestAuth"),
]

output = []

missing = []

for qid, query, symbol in QUERIES:

    if symbol not in symbols:
        missing.append(symbol)
        continue

    output.append(
        {
            "id": qid,
            "query": query,
            "relevant_chunks": [
                symbols[symbol]
            ]
        }
    )

with open("eval/queries.json","w",encoding="utf8") as f:
    json.dump(output,f,indent=4)

print(f"Generated {len(output)} queries")

if missing:
    print("\nMissing symbols:")
    for m in missing:
        print("-",m)