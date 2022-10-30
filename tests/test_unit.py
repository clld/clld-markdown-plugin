import pytest

from clld_markdown_plugin import *


@pytest.mark.parametrize(
    'model_map,renderer_map,md,substring',
    [
        (dict(LanguageTable=None), {}, '[xyz](LanguageTable#cldf:l1)', 'xyz'),
        ({}, {}, '[xyz](LanguageTable#cldf:l1)', 'The Language'),
        ({}, {}, '[xyz](LanguageTable?_anchor=abc#cldf:l1)', '#abc'),
        ({}, {}, '[xyz](LanguageTable?ids=l1,l2,l3#cldf:__all__)', ' and '),
        ({}, {}, '[xyz](ExampleTable#cldf:s1)', 'A sentence'),
        ({}, {}, '[xyz](ExampleTable?as_link#cldf:s1)', 'href='),
        ({}, {}, '[xyz](ExampleTable?ids=s1#cldf:__all__)', ''),
        ({}, {}, '[xyz](NopeTable#cldf:1)', 'NopeTable'),
        ({}, {}, '[xyz](http://example.org)', 'http://example.org'),
    ]
)
def test_markdown(model_map, renderer_map, md, substring, dbsession, req_factory):
    assert substring in markdown(
        req_factory(dict(model_map=model_map, renderer_map=renderer_map)), md, session=dbsession)
