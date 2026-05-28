#import "./code/plugin/index.typ": *
#import "./code/package/index.typ": *
#import "./code/components/index.typ": *

#show: layout.init
#show: style.use-par
#show: style.use-text
#show: nobreak.apply

#set document(
	title: meta.get("title"),
	author: meta.get("author"),
	description: meta.get("description"),
	keywords: meta.get("keywords")
)

#set text(lang: meta.get("language[ISO-639]"))

/// ========= BOOK CONTENT START ========= ///

= #title()

#line(length: 100%)

#catalog-card.new("", (
	"author":         meta.get("author"),
	"title":          meta.property("Аннотация").at(0),
	"description":    meta.property("Аннотация").at(1),
	"ISBN":           meta.property("ISBN"),
	"Авторский знак": meta.property("Библиографическая информация").at("Авторский знак"),
	"ББК":           meta.property("Библиографическая информация").at("ББК"),
	"УДК":           meta.property("Библиографическая информация").at("УДК"),
))

#chapter.read(
	"Chapter Name",
	"Chapter Name",
)

/// ========= BOOK CONTENT END ========= ///
