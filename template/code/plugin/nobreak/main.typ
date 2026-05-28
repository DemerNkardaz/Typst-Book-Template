// code/plugin/no-break/main.typ

#let data = yaml("../../../settings/nobreak.yml")

#let _options = data.at("options", default: (:))
#let _words = data.at("words", default: ())

#let _create-rule(words, options) = {
  if words.len() == 0 { return none }

  let case-sensitive = options.at("case-sensitive", default: false)
  let partial-match = options.at("partial-match", default: true)

  let escaped = words.map(word => {
    word
      .replace("\\", "\\\\")
      .replace(".", "\\.")
      .replace("*", "\\*")
      .replace("+", "\\+")
      .replace("?", "\\?")
      .replace("(", "\\(")
      .replace(")", "\\)")
      .replace("[", "\\[")
      .replace("]", "\\]")
      .replace("{", "\\{")
      .replace("}", "\\}")
      .replace("^", "\\^")
      .replace("$", "\\$")
      .replace("|", "\\|")
  })

  let case-flag = if case-sensitive { "" } else { "(?i)" }
  let suffix = if partial-match { "\\w*" } else { "" }

  regex(case-flag + "\\b(" + escaped.join("|") + ")" + suffix)
}

#let _pattern = _create-rule(_words, _options)

#let apply(content) = {
  if _pattern == none { return content }
  show _pattern: match => box[#match.text]
  content
}
