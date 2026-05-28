#let _properties = yaml("../../../meta/property.yml")
#let _book = yaml("../../../meta/book.yml")

#let property(name) = {
  if name in _properties{
    _properties.at(name)
  }
}

#let get(name) = {
	if name in _book {
		_book.at(name)
	}
}
