#!/usr/bin/env python3
# coding=utf-8
"""
Borrowed and updated from
https://adamj.eu/tech/2014/09/21/using-ipython-notebook-to-write-jekyll-blog-posts/

"""

from __future__ import print_function

import functools
import json
import os
import re
import sys
import io


def main():
    if len(sys.argv) != 2:
        print("Usage: {} filename.ipynb".format(sys.argv[0]))
        print("Will create filename.md.")
        return 1

    filename = sys.argv[1]
    notebook = json.load(open(filename))
    dirname = os.path.dirname(filename)
    title = os.path.splitext(os.path.basename(filename))[0]

    out_filename = os.path.join(
        dirname,
        "{}.md".format(title)
    )
    out_content = ""
    mem_file = io.StringIO()
    write = functools.partial(print, file=mem_file)

    cells = notebook['cells']

    for cell in cells:
        try:
            if cell['cell_type'] == 'markdown':
                # Easy
                write(''.join(cell['source']))
            elif cell['cell_type'] == 'code':

                write("{% capture content %}{% highlight python %}")
                write(''.join(cell['source']))
                write("{% endhighlight %}{% endcapture %}")

                write("{{% include notebook-cell.html execution_count={} content=content type='input' %}}".format(
                    cell['execution_count'],
                ))

                unknown_types = {o['output_type'] for o in cell['outputs']} - {'stream', 'execute_result'}
                if unknown_types:
                    raise ValueError("Unknown types : {}".format(", ".join(unknown_types)))

                for output in cell['outputs']:

                    if output['output_type'] == 'execute_result':
                        write("{% capture content %}{% highlight python %}")
                        write(''.join(output['data']["text/plain"]))
                        write("{% endhighlight %}{% endcapture %}")
                        write(
                            "{{% include notebook-cell.html execution_count={} "
                            "content=content type='output' %}}".format(
                                cell['execution_count'],
                            )
                        )
                    else:
                        write("<pre>")
                        if output['output_type'] == 'stream':
                            write(''.join(output['text']).strip(" \n"))

                        elif output['output_type'] == 'pyerr':
                            write('\n'.join(strip_colors(o)
                                            for o in output['traceback']).strip(" \n"))
                        write("</pre>")
        except:
            print(cell, type(cell))
            raise

        write("")

    with open(out_filename, "w") as out_file:
        out_file.write(mem_file.getvalue())

    print("{} created.".format(out_filename))


ansi_escape = re.compile(r'\x1b[^m]*m')


def strip_colors(string):
    return ansi_escape.sub('', string)


if __name__ == '__main__':
    main()
