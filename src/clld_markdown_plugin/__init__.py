"""Top-level package for clld-markdown-plugin."""
import typing
import logging

from markdown import Markdown
from pycldf.ext.markdown import CLDFMarkdownLink
from clld.db.meta import DBSession
from clld.db.models import common
from clld.web.util.helpers import rendered_sentence

log = logging.getLogger(__name__)

__author__ = "Robert Forkel, Florian Matter"
__email__ = "robert_forkel@eva.mpg.de, florianmatter@gmail.com"
__version__ = "0.2.1.dev0"
__all__ = ['markdown', 'includeme']


def settings(custom: typing.Optional[dict] = None) -> dict:
    def full_spec(spec):
        return spec if isinstance(spec, dict) else {
            'route': spec.__name__.split('.')[-1].lower() if spec else '', 'model': spec}

    res = {
        'model_map': {
            "LanguageTable": full_spec(common.Language),
            "ParameterTable": full_spec(common.Parameter),
            "ValueTable": full_spec(common.Value),
            "FormTable": full_spec(common.Unit),
            "ExampleTable": full_spec(common.Sentence),
            "ContributionTable": full_spec(common.Contribution),
            "CognatesetTable": full_spec(common.UnitParameter),
            "sources.bib": full_spec(common.Source),
            "Source": full_spec(common.Source),
        },
        'renderer_map': {
            "ExampleTable": render_ex,
        },
        "extensions": [
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
        ]
    }
    custom = custom or {}
    for key in res:
        if key == 'model_map':
            for k, v in custom.get(key, {}).items():
                res[key][k] = full_spec(v)
        elif key == "renderer_map":
            res[key].update(custom.get(key, {}))
        elif key == "extensions":
            res[key].extend(custom.get(key, []))
    return res


def includeme(config):
    """
    Called when the plugin is included in a clld app via `config.include('clld_markdown_plugin')`.

    Merges default and custom configuration for the plugin in the app's deployment settings under
    key 'clld_markdown_plugin'.

    .. seealso:: https://docs.pylonsproject.org/projects/pyramid/en/latest/api/registry.html\
    #pyramid.registry.Registry.settings

    :param config: `pyramid.config.Configurator`
    :return: `pyramid.config.Configurator` with updated settings for `clld_markdown_plugin`.
    """
    config.registry.settings[__name__] = settings(
        config.registry.settings.get(__name__))
    return config


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
        return decorate(md_str) if decorate else md_str


def render_ex(req, objid, table, session, ids=None, **kw):
    if objid == "__all__":
        if ids:
            ex_strs = [
                render_ex(req, mid, table, session, subexample=True) for mid in ids[0].split(",")
            ]
            return '\n\n'.join(ex_strs)
    return rendered_sentence(session.query(common.Sentence).filter(common.Sentence.id == objid)[0])


def markdown(req, s: str, session=None) -> str:
    """
    :param req:
    :param s:
    :param permalink:
    :param session:
    :return: `str` containing HTML formatting.
    """
    if __name__ not in req.registry.settings:  # pragma: no cover
        raise KeyError(
            '{} must be included in the app config to use the "markdown" function.'.format(
                __name__))
    settings = req.registry.settings[__name__]

    def repl(ml):
        if ml.is_cldf_link:
            try:
                table = ml.table_or_fname
                if table in settings['renderer_map'] and "as_link" not in ml.parsed_url_query:
                    return settings['renderer_map'][table](
                        req, ml.objid, table, session or DBSession, **ml.parsed_url_query)
                elif table in settings['model_map']:
                    decorate = settings['model_map'][table].get("decorate", None)
                    return link_entity(
                        req,
                        ml.objid,
                        settings['model_map'][table]["route"],
                        settings['model_map'][table]["model"],
                        session or DBSession,
                        decorate=decorate,
                        **ml.parsed_url_query,
                    )
                log.error(f"Can't handle [{ml.objid}] ({table}).")
                return f"{table}:{ml.objid}"
            except:  # noqa: E722
                return ml.label
        return ml

    return Markdown(extensions=settings["extensions"]).convert(CLDFMarkdownLink.replace(s, repl))
