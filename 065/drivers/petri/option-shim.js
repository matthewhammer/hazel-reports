// The one runtime helper report 046's ReScript and Melange outputs call, Some(x) for an option (ReScript's
// Primitive_option.some and Melange's Caml_option.some, which are the same): x itself, unless x is undefined or itself a
// nested None, which are boxed. Written here so the bench needs no npm packages.
export function some(x) {
  if (x === undefined) return { BS_PRIVATE_NESTED_SOME_NONE: 0 };
  if (x !== null && x.BS_PRIVATE_NESTED_SOME_NONE !== undefined) return { BS_PRIVATE_NESTED_SOME_NONE: x.BS_PRIVATE_NESTED_SOME_NONE + 1 | 0 };
  return x;
}
