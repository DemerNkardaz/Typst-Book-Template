#import "./preamble.typ": *

#pagebreak()

#place(
	center + horizon,
	[
		#image(meta.get-asset("Логотип серии"), width: 128pt + 32pt)

		#text(size: 32pt)[#meta.get("book.series")]

		#text(size: 24pt)[#meta.get("book.cycle")]

		#text(size: 16pt)[#meta.get("book.title")]

		#text(size: 12pt)[Том  #meta.get("book.volume")]
	]
)

#pagebreak()
