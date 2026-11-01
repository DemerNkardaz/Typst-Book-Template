#import "../../plugin/lib.typ": *

#let book-title(
	foretitle-content: "Foretitle",
	title-content: "Title",
	author-content: "Author",
	publisher-content: ("Publisher", "Origin", v(2em), 2026),
	publisher-spacing: 1em
) = {
	place(
		center + horizon,
		foretitle-content
	)

	pagebreak()

	place(center, text(author-content))
	place(center + horizon,
		text(size: 18pt)[#title(title-content)]
	)
	place(center + bottom, stack(
		dir: ttb,
		spacing: publisher-spacing,
		..publisher-content.map(item => {
			if type(item) == int or type(item) == float {
				str(item)
			} else {
				item
			}
		})
	))

	pagebreak()
}

#book-title()
