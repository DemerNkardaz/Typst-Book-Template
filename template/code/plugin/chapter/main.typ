#let read(..args) = {
  let items = args.pos()
  let i = 0
  while i < items.len() {
    let number = items.at(i)
    let name = items.at(i + 1)

    include(
      "../../../book/chapters/[" + str(number) + "] " + name + ".typ"
    )
    i = i + 2
  }
}
