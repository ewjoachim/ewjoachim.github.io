# modification of config created here: https://gist.github.com/cscorley/9144544
try:
    from urllib.parse import quote  # Py 3
except ImportError:
    from urllib2 import quote  # Py 2
import os
import sys

"""
Adapted from http://christop.club/2014/02/21/blogging-with-ipython-and-jekyll/
"""

SCRIPT_DIR = os.path.dirname(__file__)
BLOG_DIR = os.path.dirname(SCRIPT_DIR)
POSTS_DIR = os.path.join(BLOG_DIR, "_posts")


def main(*args):
    """
    "Usage: jupyter nbconvert --to markdown --config jekyll.py <notebook>.ipynb"
    """
    file = None

    if len(args) != 1:
        print(main.__doc__.strip())
        sys.exit()

    arg = args[0]

    file = os.path.splitext(os.path.basename(arg))[0]

    config = get_config()
    config.NbConvertApp.export_format = 'markdown'
    config.MarkdownExporter.template_path = [SCRIPT_DIR]  # point this to your jekyll template file
    config.MarkdownExporter.template_file = 'nbjekyll'
    # config.Application.verbose_crash=True

    # modify this function to point your images to a custom path
    # by default this saves all images to a directory 'images' in the root of the blog directory
    def path2support(path):
        """Turn a file path into a URL"""
        return '{{ BASE_PATH }}/images/' + os.path.basename(path)

    config.MarkdownExporter.filters = {'path2support': path2support}

    if file:
        config.NbConvertApp.output_base = f.lower().replace(' ', '-')
        config.FilesWriter.build_directory = POSTS_DIR  # point this to your build directory

if __name__ == '__main__':
    main(sys.argv[1:])
