#import "./preamble.typ": *

#component.base.pre-title(entries: (
  ("text": (
    "size": 32pt,
    "content": meta.book("series"),
    "if": meta.book-has("series")
  )),
  ("text": (
    "size": 24pt,
    "content": meta.book("cycle"),
    "if": meta.book-has("cycle")
  )),
  ("text": (
    "size": 16pt,
    "content": meta.book("title")
  )),
  ("text": (
    "size": 12pt,
    "content": () => [Том #numbering("I", meta.book("volume"))],
    "if": meta.book-has("volume") and meta.book("volume") != none
  ))
))
