#import "./code/plugin/lib.typ": *
#import "./code/package/lib.typ": *
#import "./code/components/lib.typ": *

#show: layout.init
#show: style.use-par
#show: style.use-text
#show: nobreak.apply
#show: hyphenation.apply
#show: typography.apply

#set document(
	title: meta.get("title"),
	author: meta.get("author"),
	description: meta.get("description"),
	keywords: meta.get("keywords")
)

#set text(lang: meta.get("language[ISO-639]"))

/// ========= BOOK CONTENT START ========= ///

#chapter.pre-title()
#chapter.title()
#chapter.frontmatter()

= #title() <start_count>

#line(length: 100%)

#chapter.read(
	"Chapter Name",
	"Chapter Name",
)

/// ========= BOOK CONTENT END ========= ///
