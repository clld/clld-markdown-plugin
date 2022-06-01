"""Top-level package for clld-markdown-plugin."""
import logging
from cldfviz.text import CLDFMarkdownLink
from markdown import Markdown
from markdown.extensions.toc import TocExtension
from clld.db.meta import DBSession
from clld.db.models import Language, Sentence, Source, Unit, Contribution, UnitParameter
from clld.web.util.helpers import rendered_sentence
from pathlib import Path

log = logging.getLogger(__name__)

__author__ = "Robert Forkel, Florian Matter"
__email__ = "forkel@shh.mpg.de, florianmatter@gmail.com"
__version__ = "0.0.1.dev"


CUSTOM_MAP_PATH = "clld_own_markdown.py"


def includeme(config):
    pass

def comma_and_list(entries, sep1=", ", sep2=" and "):
    output = entries[0]
    for entry in entries[1:-1]:
        output += sep1 + entry
    output += sep2 + entries[-1]
    return output

def link_entity(req, objid, route, model, decorate=None, ids=None, **kwargs):
    if objid == "__all__":
        if ids:
            md_strs = [link_entity(req, mid, route, model, decorate) for mid in ids[0].split(",")]
            return comma_and_list(md_strs)
        else:
            return "Table not yet implemented"
    else:
        entity = DBSession.query(model).filter(model.id == objid)[0]
        anchor = kwargs.pop("_anchor", None)
        if isinstance(anchor, list):
            anchor = anchor[0]
        url = req.route_url(route, id=objid, _anchor=anchor, **kwargs)
        md_str = f"[{entity.name}]({url})"
        if decorate is None:
            return md_str
        else:
            return decorate(md_str)


def render_ex(req, objid, ids=None):
    if objid == "__all__":
        if ids:
            ex_strs = [render_ex(req, mid, subexample=True) for mid in ids[0].split(",")]
            return ex_strs
    sentence = DBSession.query(Sentence).filter(Sentence.id == objid)[0]
    return rendered_sentence(sentence)

def render_cogset(req, objid):
    ctx = DBSession.query(UnitParameter).get(objid)
    return "<span>Hallo</span>"
    return f"""<%util:table items="{ctx.reflexes}" args="item"">
            <%def name="head()">
                <th>Morph</th>
                <th>Language</th>
                <th>Alignment</th>
            </%def>
            <td>${h.link(request, item.counterpart)}</td>
            <td>${h.link(request, item.counterpart.language)}</td>
            <td>
                <span class="alignment">${item.alignment}</span>
            </td>
        </%util:table>"""


custom_path = Path(CUSTOM_MAP_PATH)
if custom_path.is_file():
    from clld_own_markdown import custom_model_map, custom_function_map
else:
    custom_model_map = {}
    custom_function_map = {}

model_map = {
    "LanguageTable": {"route": "language", "model": Language},
    "FormTable": {"route": "unit", "model": Unit},
    "ExampleTable": {"route": "sentence", "model": Sentence},
    "ContributionTable": {"route": "contribution", "model": Contribution},
    "CognatesetTable": {"route": "unitparameter", "model": UnitParameter},
    "ParameterTable": {"route": "unitparameter", "model": UnitParameter},
    "sources.bib": {"route": "source", "model": Source},
}

model_map.update(custom_model_map)
function_map = {"ExampleTable": render_ex, "CognatesetTable": render_cogset}
function_map.update(custom_function_map)


def markdown(req, s, permalink=True):
    def repl(ml):
        if ml.is_cldf_link:
            try:
                table = ml.table_or_fname
                if table in function_map and "as_link" not in ml.parsed_url_query:
                    return function_map[table](req, ml.objid, **ml.parsed_url_query)
                elif table in model_map:
                    decorate = model_map[table].get("decorate", None)
                    print(ml.parsed_url_query)
                    return link_entity(
                        req,
                        ml.objid,
                        model_map[table]["route"],
                        model_map[table]["model"],
                        decorate,
                        **ml.parsed_url_query
                    )
                else:
                    log.error(f"Can't handle [{ml.objid}] ({table}).")
                    return f"{table}:{ml.objid}"
            except:
                return f"[{table}:{ml.objid}]"
        return ml

    md = Markdown(
        extensions=[
            TocExtension(permalink=permalink),
            "markdown.extensions.fenced_code",
            "markdown.extensions.md_in_html",
            "markdown.extensions.tables",
            "markdown.extensions.attr_list"
        ]
    )
    return md.convert(CLDFMarkdownLink.replace(s, repl))