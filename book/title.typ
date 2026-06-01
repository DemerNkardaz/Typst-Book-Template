#import "./preamble.typ": *

#counter(page).update(1)

#component.base.title(
	foretitle: [Авантитул],
	title: meta.book("title"),
	author: meta.author("name"),
	publisher: (
		meta.publisher("name"),
		meta.publisher("origin"),
		v(1em + 2pt),
		meta.date("year")
	),
	publisher-spacing: 1em - 1pt
)
