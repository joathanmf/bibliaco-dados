"""Gera <obra>.en.jsonl.gz (uma linha por trecho) e manifest.json a partir do JSON da Free Use Bible API.

Uso: python3 -I build.py RAW_DIR CANON_YML OUT_DIR RETRIEVED_AT
"""
import gzip, hashlib, io, json, os, re, sys

RAW, CANON, OUT, RETRIEVED_AT = sys.argv[1:5]

WORKS = {
    "matthew-henry": ("Matthew Henry", "Commentary on the Whole Bible", "1706-1721"),
    "john-gill": ("John Gill", "Exposition of the Old and New Testaments", "1746-1763"),
    "adam-clarke": ("Adam Clarke", "Commentary and Critical Notes on the Holy Bible", "1810-1826"),
    "jamieson-fausset-brown": ("Robert Jamieson, A. R. Fausset, David Brown", "Commentary Critical and Explanatory on the Whole Bible", "1871"),
    "keil-delitzsch": ("Carl Friedrich Keil, Franz Delitzsch", "Biblical Commentary on the Old Testament", "1857-1878"),
    "john-calvin": ("João Calvino (John Calvin)", "Calvin's Commentaries (tradução inglesa da Calvin Translation Society)", "1844-1856"),
}


def load_canon(path):
    # Leitura mínima do db/canon.yml do app: usfm e versículos por capítulo, sem dependência de YAML
    canon, usfm = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"- usfm: (\w+)", line)
        if m:
            usfm = m.group(1)
        m = re.match(r"\s+verses: \[([\d, ]+)\]", line)
        if m and usfm:
            canon[usfm] = [int(n) for n in m.group(1).split(",")]
    assert len(canon) == 66, len(canon)
    return canon


def clean(text):
    return re.sub(r"\n{3,}", "\n\n", (text or "").replace("\r", "")).strip()


def build(work_id, canon, available):
    meta = available[work_id]
    books = json.load(open(os.path.join(RAW, work_id, "books.json"), encoding="utf-8"))["books"]
    rows, ignored = [], []
    for book in books:
        usfm = book["id"]
        if usfm not in canon:
            ignored.append(f"{usfm}: livro fora do cânon")
            continue
        verses = canon[usfm]
        intro = clean(book.get("introduction"))
        if intro:
            rows.append({"key": f"{usfm}.0.0", "book": usfm, "chapter": 0, "start_verse": 0, "end_verse": 0, "text": intro})
        if book["firstChapterNumber"] is None:
            continue
        for number in range(book["firstChapterNumber"], book["lastChapterNumber"] + 1):
            path = os.path.join(RAW, work_id, f"{usfm}_{number}.json")
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                ignored.append(f"{usfm} {number}: capítulo ausente na fonte")
                continue
            chapter = json.load(open(path, encoding="utf-8"))["chapter"]
            if not 1 <= number <= len(verses):
                if chapter["content"] or chapter.get("introduction"):
                    ignored.append(f"{usfm} {number}: capítulo fora do cânon, com texto")
                continue
            last_verse = verses[number - 1]
            intro = clean(chapter.get("introduction"))
            if intro:
                rows.append({"key": f"{usfm}.{number}.0", "book": usfm, "chapter": number, "start_verse": 0, "end_verse": 0, "text": intro})
            # Trechos por versículo inicial; o mesmo número repetido vira um trecho só
            sections = {}
            for entry in chapter["content"]:
                start = entry["number"]
                text = clean("\n\n".join(c for c in entry["content"] if isinstance(c, str)))
                if not text:
                    continue
                if not 1 <= start <= last_verse:
                    ignored.append(f"{usfm} {number}:{start}: versículo fora do cânon")
                    continue
                sections[start] = f"{sections[start]}\n\n{text}" if start in sections else text
            starts = sorted(sections)
            for i, start in enumerate(starts):
                end = starts[i + 1] - 1 if i + 1 < len(starts) else last_verse
                rows.append({"key": f"{usfm}.{number}.{start}", "book": usfm, "chapter": number,
                             "start_verse": start, "end_verse": end, "text": sections[start]})

    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.BytesIO()
    # mtime=0: o mesmo conteúdo gera sempre o mesmo .gz (e o mesmo sha256)
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0, compresslevel=9) as gz:
        gz.write(body)
    data = buffer.getvalue()
    name = f"{work_id}.en.jsonl.gz"
    open(os.path.join(OUT, name), "wb").write(data)

    author, title, years = WORKS[work_id]
    return {
        "id": work_id,
        "author": author,
        "title": title,
        "years": years,
        "language": "en",
        "license_url": meta["licenseUrl"],
        "license_notice": meta.get("licenseNotice"),
        "license_notes": meta.get("licenseNotes"),
        "website": meta["website"],
        "source": f"https://bible.helloao.org/api/c/{work_id}/books.json",
        "source_sha256": meta.get("sha256"),
        "retrieved_at": RETRIEVED_AT,
        "files": {"en": {"file": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                         "sections": len(rows), "words": len(body.decode("utf-8").split())}},
        "ignored": ignored,
    }


def main():
    canon = load_canon(CANON)
    available = {c["id"]: c for c in json.load(open(os.path.join(RAW, "available.json"), encoding="utf-8"))["commentaries"]}
    works = [build(work_id, canon, available) for work_id in WORKS]
    manifest = {"format": 1, "generated_at": RETRIEVED_AT, "works": works}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for work in works:
        f = work["files"]["en"]
        print(f"{work['id']}: {f['sections']} trechos, {f['words']} palavras, {f['bytes'] / 1e6:.1f} MB, {len(work['ignored'])} ignorados")


main()
