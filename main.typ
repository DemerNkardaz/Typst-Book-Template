#import "./code/lib.typ": *

#show: layout.init
#show: style.use-par
#show: style.use-text
#show: nobreak.apply
#show: hyphenation.apply
#show: typography.apply

#set document(
	title: meta.book("title"),
	author: meta.author("name"),
	description: meta.book("description"),
	keywords: meta.property("keywords")
)

#set text(lang: meta.property("language[ISO-639]"))

#show: word-count

/// ========= BOOK CONTENT START ========= ///

Всего слов: #total-words

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
