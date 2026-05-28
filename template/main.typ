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

#catalog-card.new(
  meta.get("title"),
  meta.get("author"),
  year: meta.get("date").year,
  note: meta.get("description"),
)

#chapter.read(
	"Chapter Name",
	"Chapter Name",
)

/// ========= BOOK CONTENT END ========= ///
