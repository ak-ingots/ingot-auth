The flows take the metadata of their run to their end: `proceed()` of a
flow and its hook `_complete()` take it, so that the end records its
change.
