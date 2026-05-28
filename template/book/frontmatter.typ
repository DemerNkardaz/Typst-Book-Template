#import "./preamble.typ": *

#catalog-card.new(name: "", (
	"author":         meta.get("author"),
	"title":          meta.property("Аннотация").at(0),
	"description":    meta.property("Аннотация").at(1),
	"ISBN":           meta.property("ISBN"),
	"Авторский знак": meta.property("Библиографическая информация").at("Авторский знак"),
	"ББК":           meta.property("Библиографическая информация").at("ББК"),
	"УДК":           meta.property("Библиографическая информация").at("УДК"),
))

#pagebreak()
