def write_pdf_metadata(
    pdf,
    book: dict[str, object],
    publisher: dict[str, object],
    prop: dict[str, object],
    version: dict[str, object],
    copyright: dict[str, object],
    author: dict[str, object],
    authors: object,
) -> None:
    with pdf.open_metadata() as meta:
        def m(key: str, val: object) -> None:
            if val is not None:
                meta[key] = str(val)

        m("prism:title", book.get("title"))
        m("prism:subtitle", book.get("sub-title"))
        m("prism:section", book.get("section"))
        m("prism:teaser", book.get("teaser"))
        m("prism:category", prop.get("genre"))
        m("prism:isPartOf", book.get("cycle"))
        m("prism:seriesTitle", book.get("series"))
        m("prism:issueName", book.get("volume-title"))
        m("prism:volume", book.get("volume"))
        m("prism:url", publisher.get("url"))
        m("prism:isbn", prop.get("ISBN"))
        m("prism:issn", prop.get("ISSN"))
        m("prism:doi", prop.get("DOI"))
        m("prism:bookEdition", version.get("edition"))
        m("dc:rights", copyright.get("notice"))
        m("prism:copyright", copyright.get("notice"))
        m("xmpRights:WebStatement", author.get("url"))
        m("xmpRights:Marked", "True" if copyright.get("enabled") else None)
        m("xmp:Nickname", book.get("title-short"))
        m("photoshop:AuthorsPosition", author.get("position"))
        m("photoshop:CaptionWriter", author.get("description-author"))

        all_authors = authors if isinstance(authors, list) else [authors]
        author_names = [
            a["name"]
            for a in all_authors
            if isinstance(a, dict) and isinstance(a.get("name"), str)
        ]
        if author_names:
            meta["dc:creator"] = author_names
