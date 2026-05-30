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
		#title[#meta.author("name")]
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
		#meta.get("publisher.name")\
		#meta.get("publisher.origin")
		#v(2pt)
		#meta.get("date.year")
	]
)


#pagebreak()
