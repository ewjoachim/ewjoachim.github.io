---
title: Dr Jekyll and Mister Jupyter
icon: flask
---

So I complety reworked the design of my [Jekyll code posts]({% post_url 2016-05-08-of-hashes-and-pythons %}) to extract them completely from [Jupyter notebooks](http://jupyter.org/).

My approach for doing this was mainly based on a [post](https://adamj.eu/tech/2014/09/21/using-ipython-notebook-to-write-jekyll-blog-posts/) by [@AdamChainz](https://twitter.com/AdamChainz) but I changed a thing or two.

What did I changed :

* I wanted the `In: [12]` to display more like in a real notebook
* I updated the expected format to Notebook v4
* I didn't need the `ipython` specific markup language

You can take my updated script and the associated Jekyll template and style from a simple [Gist](https://gist.github.com/ewjoachim/570022bb7a08403cbe525fe82bd6d3e4) or if you want to be sure to get the latest version (because I might not update the gist everytime), you'll find everything in the source of this very blog ([script](https://github.com/ewjoachim/ewjoachim.github.io/blob/master/_scripts/ipynb_to_jekyll.py), [template](https://github.com/ewjoachim/ewjoachim.github.io/blob/master/_includes/notebook-cell.html), [scss at the bottom](https://github.com/ewjoachim/ewjoachim.github.io/blob/master/css/style.scss)).

It's probably worth noting that I didn't have the opportunity to see if exceptions displayed properly, probably on a next post.

I also switched syntax highlighting to monokai.

So thanks again to [@AdamChainz](https://twitter.com/AdamChainz)
