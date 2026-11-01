#import "../../utils/lib.typ": parse-parameters, parse-value, regex-rules

#let _data = yaml("../../../settings/layout.yml")
#let _mode = sys.inputs.at("layout-mode", default: _data.at("mode"))

#let _parse-deep(value) = {
  if type(value) == str {
    parse-value(value)
  } else if type(value) == dictionary {
    value
      .pairs()
      .map(((k, v)) => (k, _parse-deep(v)))
      .to-dict()
  } else {
    value
  }
}

#let get(key, section: _mode) = {
  let keys = key.split(".")

  let value = _data.at(section, default: _data.default)

  for k in keys {
    if type(value) == dictionary and k in value {
      value = value.at(k)
      if type(value) != dictionary {
        break
      }
    } else {
      value = none
      break
    }
  }

  if value == none {
    value = _data.default
    for k in keys {
      if type(value) == dictionary and k in value {
        value = value.at(k)
        if type(value) != dictionary {
          break
        }
      } else {
        value = none
        break
      }
    }
  }

  if value != none and type(value) == str {
    return parse-value(value)
  }

  return _parse-deep(value)
}

#let _get-margin(section: _mode) = {
  let profile = _data.at(section, default: _data.default)
  let profile-margin = profile.at("page", default: (:)).at("margin", default: none)
  let default-margin = _data.default.at("page").at("margin", default: none)

  if profile-margin == none {
    return _parse-deep(default-margin)
  }

  let parsed-profile = _parse-deep(profile-margin)
  if type(parsed-profile) != dictionary {
    return parsed-profile
  }

  let parsed-default = _parse-deep(default-margin)
  let result = if type(parsed-default) == dictionary {
    parsed-default
  } else if parsed-default != none {
    (rest: parsed-default)
  } else {
    (:)
  }

  for (key, value) in parsed-profile.pairs() {
    result.insert(key, value)
  }

  result
}

#let init(body) = {
  let page-paper = get("page.paper")
  let page-size = get("page.size")
  let page-width = get("page.width")
  let page-height = get("page.height")
  let page-margin = _get-margin()
	let page-bleed = get("page.bleed")

  if page-width == none {
    page-width = page-size.at(0)
  }
  if page-height == none {
    page-height = page-size.at(1)
  }

  let page-params = if page-paper != "custom" {
    (paper: lower(page-paper))
  } else {
    (
      width: page-width,
      height: page-height,
    )
  }

	if page-bleed != none {
		page-params.insert("bleed", page-bleed)
	}

  set page(
    ..page-params,
    margin: page-margin,
  )

	set page(
		footer: context {
			let start-nodes = query(selector(<start_count>))

			if start-nodes.len() > 0 {
				let start-page = start-nodes.first().location().page()
				let current-page = here().page()

				if current-page >= start-page {
					let p = counter(page).get().first()
					let total = counter(page).final().first()

					align(center, text(8pt, [
						#numbering("1", p) | #numbering("1", total)
					]))
				} else {
					none
				}
			}
		}
	)

  body
}
