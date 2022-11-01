# clld-markdown-plugin

Render CLDF markdown in clld apps

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


### Renderer callables

The `renderer_map` configuration option for `clld_markdown_plugin` accepts a `dict` mapping
CLDF component names to Python callables with the following signature:

```python
import clld.web.app


def renderer(req: clld.web.app.ClldRequest, objid: str, table, session: clld.db.meta.DBSession, ids=None) -> str:
    """
    The returned `str` is interpreted as Markdown, so it may also include HTML.
    """
```
