#import "./preamble.typ": *

#table(
	columns: (auto, auto),
	stroke: none,
	[#text(weight: 700)[УДК]],
	[#text(weight: 700)[#meta.property("Библиографическая информация.ББК")]],

	[#text(weight: 700)[ББК]],
	[#text(weight: 700)[#meta.property("Библиографическая информация.УДК")]],

	[],
	[#text(weight: 700)[#meta.property("Библиографическая информация.Авторский знак")]]
)

#catalog-card.new(name: "", (
	"author":         meta.author("name"),
	"title":          meta.property("Бибилографическое описание").at(0),
	"description":    meta.property("Аннотация").at(0),
	"ISBN":           meta.property("ISBN"),
	"Авторский знак": meta.property("Библиографическая информация.Авторский знак"),
	"ББК":            meta.property("Библиографическая информация.ББК"),
	"УДК":            meta.property("Библиографическая информация.УДК"),
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
