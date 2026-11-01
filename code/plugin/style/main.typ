#import "../../utils/lib.typ": parse-value, regex-rules

#let _layout = yaml("../../../settings/layout.yml")
#let _input-mode = sys.inputs.at("layout-mode", default: "")
#let _mode = if _input-mode == "" {
  _layout.at("mode", default: "default")
} else {
  _input-mode
}

#let _merge-dicts(base, overrides) = {
  let result = (:)

  for (key, value) in base.pairs() {
    result.insert(key, value)
  }

  for (key, value) in overrides.pairs() {
    let inherited = result.at(key, default: none)
    let merged = if type(inherited) == dictionary and type(value) == dictionary {
      _merge-dicts(inherited, value)
    } else {
      value
    }
    result.insert(key, merged)
  }

  result
}

#let _select-mode(data) = {
  if type(data) != dictionary or "default" not in data or type(data.default) != dictionary {
    return data
  }

  _merge-dicts(
    data.default,
    data.at(_mode, default: (:)),
  )
}

#let _parse-dict(dict) = {
  let result = (:)

	if dict == none {
		return result
	}

  for (k, v) in dict {
    result.insert(k, if type(v) == dictionary {
      _parse-dict(v)
    } else {
      parse-value(v)
    })
  }
  result
}

#let _read-style(path) = _parse-dict(_select-mode(yaml(path)))

#let use(targets: "", name: "", body) = {
  let target-list = targets
    .split(" ")
    .map(t => t.trim())
    .filter(t => t.len() > 0)

	let apply-page(body) = {
		let path = if name == "" {
			"../../../style/page.yml"
		} else {
			"../../../style/page/" + name + ".yml"
		}
    let data = _read-style(path)
		set page(..data)
		body
	}

  let apply-par(body) = {
    let path = if name == "" {
      "../../../style/paragraph.yml"
    } else {
      "../../../style/paragraph/" + name + ".yml"
    }
    let data = _read-style(path)
    set par(..data)
    body
  }

  let apply-text(body) = {
    let path = if name == "" {
      "../../../style/text.yml"
    } else {
      "../../../style/text/" + name + ".yml"
    }
    let data = _read-style(path)
    set text(..data)
    body
  }

  for target in target-list {
    if target == "page" {
      body = apply-page(body)
    } else if target == "par" {
      body = apply-par(body)
    } else if target == "text" {
      body = apply-text(body)
    }
  }

  body
}

#let use-page(name: "", body) = {
	let path = if name == "" {
		"../../../style/page.yml"
	} else {
		"../../../style/page/" + name + ".yml"
	}

  let data = _read-style(path)

	set page(..data)

	body
}

#let use-par(name: "", body) = {
  let path = if name == "" {
    "../../../style/paragraph.yml"
  } else {
    "../../../style/paragraph/" + name + ".yml"
  }

  let data = _read-style(path)

  set par(..data)

  body
}

#let use-text(name: "", body) = {
  let path = if name == "" {
    "../../../style/text.yml"
  } else {
    "../../../style/text/" + name + ".yml"
  }

  let data = _read-style(path)

  set text(..data)

  body
}
