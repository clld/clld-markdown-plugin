"""Top-level package for clld-markdown-plugin."""
import logging

from markdown import Markdown
from markdown.extensions.toc import TocExtension
from cldfviz.text import CLDFMarkdownLink
from clld.db.meta import DBSession
from clld.db.models import Language, Sentence, Source, Unit, Contribution, UnitParameter
from clld.web.util.helpers import rendered_sentence

log = logging.getLogger(__name__)

__author__ = "Robert Forkel, Florian Matter"
__email__ = "forkel@shh.mpg.de, florianmatter@gmail.com"
__version__ = "0.0.1.dev"
__all__ = ['markdown', 'includeme']

default_model_map = {
    "LanguageTable": Language,
    "FormTable": Unit,
    "ExampleTable": Sentence,
    "ContributionTable": Contribution,
    "CognatesetTable": UnitParameter,
    "ParameterTable": UnitParameter,
    "sources.bib": Source,
}
model_map = {}
function_map = {}


def includeme(config):
    function_map['ExampleTable'] = render_ex
    function_map['CognatesetTable'] = render_cogset

    def full_spec(spec):
        return spec if isinstance(spec, dict) else {'route': spec.__name__.lower(), 'model': spec}

    for k, v in default_model_map.items():
        model_map[k] = full_spec(v)
    if config and 'clld_markdown_plugin' in config.registry.settings:
        for comp, spec in \
                config.registry.settings['clld_markdown_plugin'].get('model_map', {}).items():
            model_map[comp] = full_spec(spec)
        function_map.update(
            config.registry.settings['clld_markdown_plugin'].get('function_map', {}))


def comma_and_list(entries, sep1=", ", sep2=" and "):
    output = entries[0]
    for entry in entries[1:-1]:
        output += sep1 + entry
    return output + sep2 + entries[-1]


def link_entity(req, objid, route, model, session, decorate=None, ids=None, **kwargs):
    if objid == "__all__":
        if ids:
            md_strs = [
                link_entity(req, mid, route, model, session, decorate=decorate)
                for mid in ids[0].split(",")
            ]
            return comma_and_list(md_strs)
        raise NotImplementedError("Table not yet implemented")  # pragma: no cover
    else:
        entity = session.query(model).filter(model.id == objid)[0]
        anchor = kwargs.pop("_anchor", None)
        if isinstance(anchor, list):
            anchor = anchor[0]
        url = req.route_url(route, id=objid, _anchor=anchor, **kwargs)
        md_str = f"""<a class="{model.__tablename__.capitalize()}" href="{url}">{entity.name}</a>"""
        if decorate is None:
            return md_str
        else:
            return decorate(md_str)


def render_ex(req, objid, table, ids=None):
    if objid == "__all__":
        if ids:
            ex_strs = [
                render_ex(req, mid, subexample=True) for mid in ids[0].split(",")
            ]
            return ex_strs
    return rendered_sentence(DBSession.query(Sentence).filter(Sentence.id == objid)[0])


def render_cogset(req, objid, table, ids=None):
    ctx = DBSession.query(UnitParameter).get(objid)
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


def markdown(req, s, permalink=True, session=None):
    def repl(ml):
        if ml.is_cldf_link:
            try:
                table = ml.table_or_fname
                if table in function_map and "as_link" not in ml.parsed_url_query:
                    return function_map[table](req, ml.objid, table, **ml.parsed_url_query)
                elif table in model_map:
                    decorate = model_map[table].get("decorate", None)
                    return link_entity(
                        req,
                        ml.objid,
                        model_map[table]["route"],
                        model_map[table]["model"],
                        session or DBSession,
                        decorate=decorate,
                        **ml.parsed_url_query,
                    )
                else:
                    log.error(f"Can't handle [{ml.objid}] ({table}).")
                    return f"{table}:{ml.objid}"
            except:  # noqa: E722
                return ml.label
        return ml

    md = Markdown(
        extensions=[
            TocExtension(permalink=permalink),
            "markdown.extensions.fenced_code",
            "markdown.extensions.md_in_html",
            "markdown.extensions.tables",
            "markdown.extensions.attr_list",
            "markdown.extensions.footnotes",
        ]
    )
    return md.convert(CLDFMarkdownLink.replace(s, repl))
