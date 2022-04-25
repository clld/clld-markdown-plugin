"""Top-level package for clld-markdown-plugin."""
import logging
from cldfviz.text import CLDFMarkdownLink
from markdown import Markdown
from markdown.extensions.toc import TocExtension
from clld.db.meta import DBSession
from clld.db.models import Language, Sentence, Source
from clld.web.util.helpers import rendered_sentence
from pathlib import Path

log = logging.getLogger(__name__)

__author__ = "Robert Forkel, Florian Matter"
__email__ = "forkel@shh.mpg.de, florianmatter@gmail.com"
__version__ = "0.0.1.dev"


CUSTOM_MAP_PATH = "clld_own_markdown.py"


def includeme(config):
    pass


def link_entity(req, objid, route, model, decorate=None):
    entity = DBSession.query(model).filter(model.id == objid)[0]
    url = req.route_url(route, id=objid)
    md_str = f"[{entity.name}]({url})"
    if decorate is None:
        return md_str
    else:
        return decorate(md_str)


def render_ex(req, objid):
    sentence = DBSession.query(Sentence).filter(Sentence.id == objid)[0]
    return rendered_sentence(sentence)


custom_path = Path(CUSTOM_MAP_PATH)
if custom_path.is_file():
    from clld_own_markdown import custom_model_map, custom_function_map
else:
    custom_model_map = {}
    custom_function_map = {}

model_map = {
    "LanguageTable": {"route": "language", "model": Language},
    "ExampleTable": {"route": "sentence", "model": Sentence},
    "sources.bib": {"route": "source", "model": Source},
}

model_map.update(custom_model_map)
function_map = {"ExampleTable": render_ex}
function_map.update(custom_function_map)


def markdown(req, s):
    def repl(ml):
        if ml.is_cldf_link:
            try:
                table = ml.table_or_fname
                if table in function_map:
                    return function_map[table](req, ml.objid)
                elif table in model_map:
                    if "decorate" in model_map[table]:
                        decorate = model_map[table]["decorate"]
                    else:
                        decorate = None
                    return link_entity(
                        req,
                        ml.objid,
                        model_map[table]["route"],
                        model_map[table]["model"],
                        decorate,
                    )
                else:
                    log.error(f"Can't handle [{ml.objid}] ({table}).")
                    return f"{table} {ml.objid}"
            except:
                return f"[{ml.objid}] ({table}) not rendered successfully."
        return ml

    md = Markdown(
        extensions=[
            TocExtension(permalink=True),
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
        ]
    )
    return md.convert(CLDFMarkdownLink.replace(s, repl)), md
