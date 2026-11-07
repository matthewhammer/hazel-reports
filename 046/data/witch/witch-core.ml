(* the picture, as the slide's types *)
type point = float * float
type label = Plain | Anchor of string
type vertex = { at : point; label : label }
type stroke = { width : float; color : string }
type shape =
  | Polygon of { name : string; points : vertex list; stroke : stroke; fill : string }
  | Path of { name : string; points : vertex list; stroke : stroke }
type picture = shape list

(* what a view returns: Hazel's Html and Attr, as far as this view uses them *)
type attr = Create of string * string | Width of string | Height of string | Style of (string * string) list
type html = Node of string * attr list * html list | Div of attr list * html list | Text of string

(* the view *)
let num (x : float) = fixed1 x

let rec coords (vs : vertex list) =
  match vs with
  | [] -> ""
  | v :: tl -> let (x, y) = v.at in fixed1 x ^ "," ^ fixed1 y ^ " " ^ coords tl

let shape_node (s : shape) =
  match s with
  | Polygon p ->
    Node ("polygon",
      [ Create ("points", coords p.points); Create ("fill", p.fill); Create ("stroke", p.stroke.color);
        Create ("stroke-width", num p.stroke.width); Create ("stroke-linejoin", "round") ], [])
  | Path p ->
    Node ("polyline",
      [ Create ("points", coords p.points); Create ("fill", "none"); Create ("stroke", p.stroke.color);
        Create ("stroke-width", num p.stroke.width); Create ("stroke-linejoin", "round");
        Create ("stroke-linecap", "round") ], [])

let rec shape_nodes (ss : picture) =
  match ss with [] -> [] | s :: tl -> shape_node s :: shape_nodes tl

let vertices_of (s : shape) = match s with Polygon p -> p.points | Path p -> p.points

let grow ((x0, y0, x1, y1) : float * float * float * float) (v : vertex) =
  let (x, y) = v.at in
  ((if x -. 12. < x0 then x -. 12. else x0),
   (if y -. 12. < y0 then y -. 12. else y0),
   (if x +. 12. > x1 then x +. 12. else x1),
   (if y +. 12. > y1 then y +. 12. else y1))

let rec grow_all b (vs : vertex list) = match vs with [] -> b | v :: tl -> grow_all (grow b v) tl

let rec bounds b (ss : picture) = match ss with [] -> b | s :: tl -> bounds (grow_all b (vertices_of s)) tl

let rec framing (ss : picture) =
  match ss with
  | [] -> []
  | s :: tl -> (match s with Path p -> if p.name = "frame" then [ s ] else framing tl | _ -> framing tl)

let view_box (pic : picture) =
  let boxed = match framing pic with [] -> pic | f -> f in
  let start =
    match boxed with
    | [] -> (0., 0., 0., 0.)
    | s :: _ -> (match vertices_of s with [] -> (0., 0., 0., 0.) | v :: _ -> let (x, y) = v.at in (x, y, x, y))
  in
  let (x0, y0, x1, y1) = bounds start boxed in
  let (w, h) = (x1 -. x0, y1 -. y0) in
  let (w2, h2) = if w *. 440. > h *. 320. then (w, w *. 440. /. 320.) else (h *. 320. /. 440., h) in
  num (x0 -. (w2 -. w) /. 2.) ^ " " ^ num (y0 -. (h2 -. h) /. 2.) ^ " " ^ num w2 ^ " " ^ num h2

(* the view's work once its splice is evaluated: Hazel's `case r | Some(Val(pic)) => ... | _ => ...` *)
let view (r : picture option) =
  match r with
  | Some pic ->
    Node ("svg",
      [ Create ("viewBox", view_box pic); Width "320"; Height "440";
        Style [ ("border", "1px solid #ccc"); ("background", "#fafafa") ] ],
      shape_nodes pic)
  | None ->
    Div ([ Style [ ("font-family", "var(--code-font)"); ("font-size", "0.8em") ] ], [ Text "no picture yet" ])

(* (not timed) a drawing as markup, to compare with hazel-jit's; the picture's strings need no escaping *)
let rec join f xs = match xs with [] -> "" | x :: tl -> f x ^ join f tl
let rec join_sep f sep xs = match xs with [] -> "" | [ x ] -> f x | x :: tl -> f x ^ sep ^ join_sep f sep tl
let attr_markup a =
  match a with
  | Create (k, v) -> " " ^ k ^ "=\"" ^ v ^ "\""
  | Width v -> " width=\"" ^ v ^ "\""
  | Height v -> " height=\"" ^ v ^ "\""
  | Style kvs -> " style=\"" ^ join_sep (fun (k, v) -> k ^ ": " ^ v) ";" kvs ^ "\""
let rec markup h =
  match h with
  | Node (tag, attrs, kids) -> "<" ^ tag ^ join attr_markup attrs ^ ">" ^ join markup kids ^ "</" ^ tag ^ ">"
  | Div (attrs, kids) -> markup (Node ("div", attrs, kids))
  | Text s -> s
