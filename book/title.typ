#import "./preamble.typ": *

#counter(page).update(1)

#component.base.book-title(
	foretitle-content: [Авантитул],

	title-content: meta.book(
		"title",
		fallback: locale.get("fallback.title")
	),

	author-content: meta.author(
		"name",
		fallback: locale.get("fallback.author")
	),

	publisher-content: (
		meta.publisher(
			"name",
			fallback: locale.get("fallback.publisher")
		),
		meta.publisher(
			"origin",
			fallback: locale.get("fallback.publisher-origin")
		),
		v(1em + 2pt),
		meta.date(
			"year",
			fallback: 2026
		)
	),

	publisher-spacing: 1em - 1pt
)
