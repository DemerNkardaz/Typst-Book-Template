#import "./preamble.typ": *

#counter(page).update(1)

#place(
	center + horizon,
	[
		Авантитул
	]
)

#pagebreak()

#place(
	center,
	[
		#title[#meta.get("author")]
	]
)


#place(
	center + horizon,
	[
		#text(size: 18pt)[#title()]
	]
)


#place(
	bottom + center,
	[
		#meta.get("publisher")\
		#meta.get("publisher-origin")
	]
)


#pagebreak()
