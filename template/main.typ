#import "./code/plugin/index.typ": *
#import "./code/package/index.typ": *

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

#chapter.read(
	1, "Chapter Name",
	2, "Chapter Name",
)

/// ========= BOOK CONTENT END ========= ///
