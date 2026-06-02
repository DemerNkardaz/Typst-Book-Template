#import "./preamble.typ": *

#component.base.ГОСТ-Р-7-0-4-2020.блок-классификации(
	УДК: meta.property("УДК"),
	ББК: meta.property("ББК"),
	Авторский-знак: meta.property("Авторский знак")
)

#component.catalog-card.new(name: "", (
	"author":         meta.author("name"),
	"title":          meta.property("Бибилографическое описание").at(0),
	"description":    meta.property("Аннотация").at(0),
	"ISBN":           meta.property("ISBN"),
	"Авторский знак": meta.property("Авторский знак"),
	"ББК":            meta.property("ББК"),
	"УДК":            meta.property("УДК"),
))

#place(
	bottom + center,
  float: true,
	[
		#block(
			width: 100%,
			inset: (x: 6pt, y: 0pt)
		)[
			#table(
				columns: (1fr, 1fr),
				rows: 1,
				align: (left, right),
				stroke: none,

				[#meta.property("ISBN")],
				[#sym.copyright #meta.author("name"), #meta.date("year")]
			)
		]
	]
)

#pagebreak()
