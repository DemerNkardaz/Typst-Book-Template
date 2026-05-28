#let _data = yaml("../../../settings/typography-rules.yml")

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
  let m = matched.match(regex("^(?:" + pattern + ")$"))
  let captures = if m != none { m.captures } else { () }
  let segments = _parse-inline-evals(template)
  let parts = ()
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
  let rule = rules.first()
  let rest-rules = rules.slice(1)
  let pattern = rule.at(0)
  show regex(pattern): it => _build-replacement(rule.at(1), it.text, pattern)
  _apply-rules(rest-rules, body)
}

#let apply(content) = {
  if _data.len() == 0 { return content }
  _apply-rules(_data, content)
}
