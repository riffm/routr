"""

    wk.doc -- extension for generating documentation with sphinx
    ============================================================

"""

from docutils import nodes
from docutils.statemachine import ViewList

from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.nodes import nested_parse_with_titles
from sphinxcontrib import httpdomain

from routr.utils import import_string
from routr.schema import Method
from routr import RouteList

__all__ = ("AutoRoutrDirective",)

def traverse_routes(route, path="/"):
    """ Traverse routes by flatten them"""
    if isinstance(route, RouteList):
        return [(m, p, r)
            for subroute in route.routes
            for (m, p, r) in traverse_routes(
                subroute,
                path=join_path(path, subroute))]
    else:
        return [route.method, path, route)]

def join_path(a, r):
    if not r.prefix:
        return a
    b = r.prefix.pattern
    if a.endswith("/"):
        a = a[:-1]
    if b.startswith("/"):
        b = b[1:]
    return a + "/" + b

def http_directive(method, path, content):
    """ Construct line for http directive from httpdomain

    :copyright: (c) Hong Minhee
    """
    method = method.lower().strip()
    if isinstance(content, basestring):
        content = content.splitlines()
    yield ""
    yield ".. http:%s:: %s" % (method, path)
    yield ""
    for line in content:
        yield "   " + line
    yield ""

class AutoRoutrDirective(Directive):
    """ Directive for generating docs from routr routes

    Based on code from httpdomain.autoflask by Hong Minhee.
    """

    has_content = True
    requied_argument = 1
    option_spec = {}

    def make_rst(self):
        routes = import_string(self.content.data[0])
        for method, path, route in traverse_routes(routes):
            docstring = prepare_docstring(route.view.__doc__ or "")
            for line in http_directive(method, path, docstring):
                yield line

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, "<autoflask>")
        nested_parse_with_titles(self.state, result, node)
        return node.children

def setup(app):
    if "http" not in app.domains:
        httpdomain.setup(app)
    app.add_directive("autoroutr", AutoRoutrDirective)

