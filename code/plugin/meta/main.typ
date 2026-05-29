#import "../../utils/main.typ": resolve-path

#let _properties = yaml("../../../meta/property.yml")
#let _book = yaml("../../../meta/book.yml")

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
      let resolved = resolve-path(_book, key-path)
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
  let val = resolve-path(_properties, name)
  if val != none {
    if type(val) == array {
      val.map(_interpolate)
    } else {
      _interpolate(val)
    }
  }
}

#let get(name) = {
  let val = resolve-path(_book, name)
  if val != none {
    _interpolate(val)
  }
}
