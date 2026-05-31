#import "./preamble.typ": *

#pagebreak()


#place(
	center + horizon,
	[
		#image(meta.get-asset("Логотип серии"), width: 128pt + 32pt)

		#text(size: 32pt)[#meta.book("series")]

		#text(size: 24pt)[#meta.book("cycle")]

		#text(size: 16pt)[#meta.book("title")]

		#text(size: 12pt)[#(
			if meta.book-has("volume") and meta.book("volume") != none {
				[Том #numbering("I", meta.book("volume"))]
			}
		)]
	]
)


#pagebreak()
