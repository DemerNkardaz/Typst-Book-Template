#import "./preamble.typ": *

#pagebreak()

#place(
	center + horizon,
	[
		#image("../assets/logo-series.svg", width: 128pt + 32pt)

		#text(size: 32pt)[#meta.get("series")]

		#text(size: 24pt)[#meta.get("cycle")]

		#text(size: 16pt)[#meta.get("title")]

		#text(size: 12pt)[Том  #meta.get("volume")]
	]
)

#pagebreak()
