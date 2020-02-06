# embedmath

Python-based command line tool to process Markdown documents with latex math sections, rendering those math sections as SVG images and embedding them into the document.  Note that these embedded images are much larger than the bare latex so this shouldn't be used if your platform supports markdown with latex.  This is primarily of use when you're writing markdown for a service that doesn't support latex and will not support latex.  This uses pandoc to convert markdown into itself so you may see some elements change from your variant of markdown to the pandoc variant, so it might require a little bit of playing around to get things working how you want them to work.  The `embedmath` tool requires the following be in your path:

 * pandoc 
 * latex
 * dvisvgm (usually part of latex)

As a usage example, `embedmath file.md` will convert all math sections of `file.md` into `<img embedmath-tex="..." src="data:image/svg+xml;base64,...">` SVG tags and return the rendered file to the `stdout`.  Inline math is rendered directly to an image, but display math has the image wrapped in a `<p>` element.

Similarly to `embedmath`, you can `unembedmath` a markdown file that's been encoded with `embedmath`.  This operation replaces the images with the content in the `embedmath-tex` property.  

## Example

```markdown
---
title: Document
---

We recommend $A$-optimal allocation. Let $N$ be the total number of samples and
$n = N/m$ represent the sample size in the balanced case. We define $k$
to be
$$
k=\frac{-2m + \sqrt{m^3 + 2m^2 + m}}{m(m-1)}n~.
$$
The optimal sample sizes are then
$$
n_\mathrm{control} = n + mk
\quad\text{and}\quad
n_i = n - k \quad\text{for}\quad i=1,\ldots,m~.
$$
``` 
converts to
```markdown
---
title: Document
---

We recommend
<img embedmath-tex="$A$" src="data:image/svg+xml;base64,...">-optimal
allocation. Let
<img embedmath-tex="$N$" src="data:image/svg+xml;base64,...">
be the total number of samples and
<img embedmath-tex="$n = N/m$" src="data:image/svg+xml;base64,...">
represent the sample size in the balanced case. We define
<img embedmath-tex="$k$" src="data:image/svg+xml;base64,...">
to be
<p align="center" style="clear: both;" embedmath-tex="$$\nk=\\frac{-2m + \\sqrt{m^3 + 2m^2 + m}}{m(m-1)}n~.\n$$"><img src="data:image/svg+xml;base64,..."></p>
The optimal sample sizes are then
<p align="center" style="clear: both;" embedmath-tex="$$\nn_\\mathrm{control} = n + mk\n\\quad\\text{and}\\quad\nn_i = n - k \\quad\\text{for}\\quad i=1,\\ldots,m~.\n$$"><img src="data:image/svg+xml;base64,..."></p>
``` 

## Pandoc Filters

You can use the pandoc filters as part of a pandoc processing pipeline.  The filters are available at `_embedmath_encoding_filter` and `_embedmath_decoding_filter`.
