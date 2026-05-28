#let new(title, author, year: none, note: none, style: none) = [
  #rect(
    width: 100%,
    height: auto,
    stroke: 0.5pt,
    radius: 2pt,
    inset: 12pt,
    [
      #text(size: 11pt, weight: "bold")[#title] \
      #text(size: 9pt)[by #author]

      #if year != none [
        #text(size: 8pt)[Year: #year]
      ]

      #v(4pt)

      #if note != none [
        #text(size: 8pt)[#note]
      ]

      #v(6pt)
    ]
  )
]
