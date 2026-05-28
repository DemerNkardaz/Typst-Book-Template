#let _properties = yaml("../../../meta/property.yml")
#let _book = yaml("../../../meta/book.yml")

#let _resolve-path(dict, key-path) = {
  let parts = key-path.split(".")
  let node = dict
  for part in parts {
    if type(node) == dictionary and part in node {
      node = node.at(part)
    } else {
      return none
    }
  }
  node
}

#let _interpolate(val) = {
  if type(val) == str {
    let result = ""
    let rest = val
    while rest.len() > 0 {
      let start = rest.position("#(")
      if start == none {
        result += rest
        break
      }
      result += rest.slice(0, start)
      rest = rest.slice(start + 2)
      let end = rest.position(")")
      if end == none {
        result += "#(" + rest
        break
      }
      let key-path = rest.slice(0, end)
      rest = rest.slice(end + 1)
      let resolved = _resolve-path(_book, key-path)
      if resolved != none {
        result += str(resolved)
      }
    }
    result
  } else {
    val
  }
}

#let property(name) = {
  if name in _properties {
    let val = _properties.at(name)
    if type(val) == array {
      val.map(_interpolate)
    } else {
      _interpolate(val)
    }
  }
}
#let get(name) = {
	if name in _book {
		_book.at(name)
	}
}
