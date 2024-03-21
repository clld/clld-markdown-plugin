# clld-markdown-plugin

Render [CLDF markdown](https://github.com/cldf/cldf/blob/master/extensions/markdown.md) in clld apps

## Usage

Include (and configure the plugin) in your app's `main` function:
```python
def main(global_config, **settings):
    settings['clld_markdown_plugin'] = {
        'model_map': {'ValueTable': common.ValueSet},
        'function_map': {}
    }
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    ...
    config.include('clld_markdown_plugin')
```

Then you can use `clld_markdown_plugin.markup` as follows in your templates:
```html
<%! from clld_markdown_plugin import markdown %>

${markdown(req, '[x](LanguageTable#cldf:abad1241)')|n}
```

By default, links to objects in the CLDF dataset will be rendered as HTML links to the corresponding
object's details page in the clld app.


### Configuration

The plugin can be configured via the following four configuration options:

- `model_map`: A `dict` mapping CLDF component names to DB model classes defined for the app. This
  allows for a flexible mapping between CLDF components and the clld DB classes.
- `renderer_map`: See below for details.
- `extensions`: A list of [markdown extensions](https://python-markdown.github.io/extensions/#officially-supported-extensions)
  in dot notation, to be activated when calling the `markdown` function.
- `keep_link_labels`: A `boolean` indicating whether to keep link labels as they appear in the
  CLDF Markdown text. By default (`False`), labels will be substituted using the linked object's
  name.


#### Renderer callables

The `renderer_map` configuration option for `clld_markdown_plugin` accepts a `dict` mapping
CLDF component names to Python callables with the following signature:

```python
import clld.web.app


def renderer(req: clld.web.app.ClldRequest, objid: str, table, session: clld.db.meta.DBSession, ids=None) -> str:
    """
    The returned `str` is interpreted as Markdown, so it may also include HTML.
    """
```
