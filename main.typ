#import "./code/lib.typ": *

#set text(
	lang: meta.property("locale", fallback: "en-US").slice(0, 2),
	region: meta.property("locale", fallback: "en-US").slice(3)
)

#show: layout.init
#show: style.use-par
#show: style.use-text
#show: nobreak.apply
#show: hyphenation.apply
#show: typography.apply

#set document(
	title: meta.book("title", fallback: locale.get("fallback.title")),
	author: meta.author("name", fallback: locale.get("fallback.author")),
	description: meta.book("description", fallback: ""),
	keywords: meta.property("keywords", fallback: [])
)
#show: word-count

/// ========= BOOK CONTENT START ========= ///

Всего слов: #total-words

#meta.author("naаme", fallback: locale.get("fallback.author"))

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
