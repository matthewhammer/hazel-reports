// ^report(46): the Witch slide's ^picture view, in ReScript as the Hazel is written (witch.hz, Drawing.^picture)

// the picture, as the slide's types
type point = (float, float)
type label = Plain | Anchor(string)
type vertex = {at: point, label: label}
type stroke = {width: float, color: string}
type shape =
  | Polygon({name: string, points: list<vertex>, stroke: stroke, fill: string})
  | Path({name: string, points: list<vertex>, stroke: stroke})
type picture = list<shape>

// what a view returns: Hazel's Html and Attr, as far as this view uses them
type attr = Create(string, string) | Width(string) | Height(string) | Style(list<(string, string)>)
type rec html = Node(string, list<attr>, list<html>) | Div(list<attr>, list<html>) | Text(string)

// the view
let num = x => Float.toFixed(x, ~digits=1)

let rec coords = (vs: list<vertex>) =>
  switch vs {
  | list{} => ""
  | list{v, ...tl} =>
    let (x, y) = v.at
    Float.toFixed(x, ~digits=1) ++ "," ++ Float.toFixed(y, ~digits=1) ++ " " ++ coords(tl)
  }

let shapeNode = s =>
  switch s {
  | Polygon(p) =>
    Node(
      "polygon",
      list{
        Create("points", coords(p.points)),
        Create("fill", p.fill),
        Create("stroke", p.stroke.color),
        Create("stroke-width", num(p.stroke.width)),
        Create("stroke-linejoin", "round"),
      },
      list{},
    )
  | Path(p) =>
    Node(
      "polyline",
      list{
        Create("points", coords(p.points)),
        Create("fill", "none"),
        Create("stroke", p.stroke.color),
        Create("stroke-width", num(p.stroke.width)),
        Create("stroke-linejoin", "round"),
        Create("stroke-linecap", "round"),
      },
      list{},
    )
  }

let rec shapeNodes = (ss: picture) =>
  switch ss {
  | list{} => list{}
  | list{s, ...tl} => list{shapeNode(s), ...shapeNodes(tl)}
  }

let verticesOf = s =>
  switch s {
  | Polygon(p) => p.points
  | Path(p) => p.points
  }

let grow = ((x0, y0, x1, y1), v: vertex) => {
  let (x, y) = v.at
  (
    x -. 12. < x0 ? x -. 12. : x0,
    y -. 12. < y0 ? y -. 12. : y0,
    x +. 12. > x1 ? x +. 12. : x1,
    y +. 12. > y1 ? y +. 12. : y1,
  )
}

let rec growAll = (b, vs) =>
  switch vs {
  | list{} => b
  | list{v, ...tl} => growAll(grow(b, v), tl)
  }

let rec bounds = (b, ss: picture) =>
  switch ss {
  | list{} => b
  | list{s, ...tl} => bounds(growAll(b, verticesOf(s)), tl)
  }

let rec framing = (ss: picture) =>
  switch ss {
  | list{} => list{}
  | list{s, ...tl} =>
    switch s {
    | Path(p) => p.name == "frame" ? list{s} : framing(tl)
    | _ => framing(tl)
    }
  }

let viewBox = (pic: picture) => {
  let boxed = switch framing(pic) {
  | list{} => pic
  | f => f
  }
  let start = switch boxed {
  | list{} => (0., 0., 0., 0.)
  | list{s, ..._} =>
    switch verticesOf(s) {
    | list{} => (0., 0., 0., 0.)
    | list{v, ..._} =>
      let (x, y) = v.at
      (x, y, x, y)
    }
  }
  let (x0, y0, x1, y1) = bounds(start, boxed)
  let (w, h) = (x1 -. x0, y1 -. y0)
  let (w2, h2) = w *. 440. > h *. 320. ? (w, w *. 440. /. 320.) : (h *. 320. /. 440., h)
  num(x0 -. (w2 -. w) /. 2.) ++ " " ++ num(y0 -. (h2 -. h) /. 2.) ++ " " ++ num(w2) ++ " " ++ num(h2)
}

// the view's work once its splice is evaluated: Hazel's `case r | Some(Val(pic)) => ... | _ => ...`
let view = (r: option<picture>) =>
  switch r {
  | Some(pic) =>
    Node(
      "svg",
      list{
        Create("viewBox", viewBox(pic)),
        Width("320"),
        Height("440"),
        Style(list{("border", "1px solid #ccc"), ("background", "#fafafa")}),
      },
      shapeNodes(pic),
    )
  | None =>
    Div(
      list{Style(list{("font-family", "var(--code-font)"), ("font-size", "0.8em")})},
      list{Text("no picture yet")},
    )
  }

// (not timed) the picture from the test's JSON, and a drawing as markup, to compare with hazel-jit's
type jsShape = {
  kind: string,
  name: string,
  points: array<(float, float, Nullable.t<string>)>,
  stroke: stroke,
  fill: Nullable.t<string>,
}

let pictureOf = (shapes: array<jsShape>): picture =>
  shapes
  ->Array.map(s => {
    let points =
      s.points
      ->Array.map(((x, y, l)) => {
        at: (x, y),
        label: switch Nullable.toOption(l) {
        | Some(n) => Anchor(n)
        | None => Plain
        },
      })
      ->List.fromArray
    s.kind == "Polygon"
      ? Polygon({name: s.name, points, stroke: s.stroke, fill: Nullable.getOr(s.fill, "")})
      : Path({name: s.name, points, stroke: s.stroke})
  })
  ->List.fromArray

let esc = s =>
  s
  ->String.replaceAll("&", "&amp;")
  ->String.replaceAll("\"", "&quot;")
  ->String.replaceAll("<", "&lt;")

let attrMarkup = a =>
  switch a {
  | Create(k, v) => " " ++ k ++ "=\"" ++ esc(v) ++ "\""
  | Width(v) => " width=\"" ++ esc(v) ++ "\""
  | Height(v) => " height=\"" ++ esc(v) ++ "\""
  | Style(kvs) =>
    " style=\"" ++
    esc(kvs->List.map(((k, v)) => k ++ ": " ++ v)->List.toArray->Array.join(";")) ++ "\""
  }

let rec markup = h =>
  switch h {
  | Node(tag, attrs, kids) =>
    "<" ++
    tag ++
    attrs->List.map(attrMarkup)->List.toArray->Array.join("") ++
    ">" ++
    kids->List.map(markup)->List.toArray->Array.join("") ++
    "</" ++
    tag ++ ">"
  | Div(attrs, kids) => markup(Node("div", attrs, kids))
  | Text(s) => esc(s)
  }
