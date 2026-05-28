#let _data = yaml("../../../settings/typography-rules.yml")

#let _storage = if "storage" in _data { _data.storage } else { (:) }
#let _rules   = if "rules"   in _data { _data.rules   } else { _data }

#let _resolve-storage(s) = {
  let rest = s
  let out  = ""
  while rest != "" {
    let idx = rest.position(regex("\\$\\{"))
    if idx == none {
      out  = out + rest
      rest = ""
    } else {
      out  = out + rest.slice(0, idx)
      let after = rest.slice(idx + 2)
      let close = after.position("}")
      if close == none {
        out  = out + rest.slice(idx)
        rest = ""
      } else {
        let key-raw = after.slice(0, close)
        let splat   = key-raw.ends-with("*")
        let key     = if splat { key-raw.slice(0, key-raw.len() - 1) } else { key-raw }
        let val     = if key in _storage { _storage.at(key) } else { "${" + key-raw + "}" }
        let resolved = if type(val) == array {
          if splat { val.join("") } else { val.join("|") }
        } else {
          str(val)
        }
        out  = out + resolved
        rest = after.slice(close + 1)
      }
    }
  }
  out
}

#let resolved = _resolve-storage("(\\d)[ ](${temperature-scales})")

#resolved

#let _parse-inline-evals(s) = {
  let segments = ()
  let rest = s
  while rest != "" {
    let idx = rest.position(regex("#\("))
    if idx == none {
      segments.push((type: "str", value: rest))
      rest = ""
    } else {
      if idx > 0 {
        segments.push((type: "str", value: rest.slice(0, idx)))
      }
      let after = rest.slice(idx + 2)
      let close = after.position(")")
      if close == none {
        segments.push((type: "str", value: rest.slice(idx)))
        rest = ""
      } else {
        segments.push((type: "eval", value: after.slice(0, close)))
        rest = after.slice(close + 1)
      }
    }
  }
  segments
}

#let _build-replacement(template, matched, pattern) = {
  let m        = matched.match(regex("^(?:" + pattern + ")$"))
  let captures = if m != none { m.captures } else { () }
  let segments = _parse-inline-evals(template)
  let parts    = ()
  for seg in segments {
    if seg.type == "eval" {
      parts.push(eval(seg.value, scope: (sym: sym)))
    } else {
      let s = seg.value
      s = s.replace("$0", matched)
      let i = 1
      for cap in captures {
        s = s.replace("$" + str(i), if cap == none { "" } else { cap })
        i += 1
      }
      parts.push(s)
    }
  }
  parts.join()
}

#let _apply-rules(rules, body) = {
  if rules.len() == 0 { return body }
  let rule        = rules.first()
  let rest-rules  = rules.slice(1)
  let pattern     = _resolve-storage(rule.at(0))
  let replacement = _resolve-storage(rule.at(1))
  show regex(pattern): it => _build-replacement(replacement, it.text, pattern)
  _apply-rules(rest-rules, body)
}

#let apply(content) = {
  if _rules.len() == 0 { return content }
  _apply-rules(_rules.rev(), content)
}
