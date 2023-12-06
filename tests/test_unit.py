import pytest

from clld_markdown_plugin import *


@pytest.mark.parametrize(
    'model_map,renderer_map,md,substring,notsubstring',
    [
        (dict(LanguageTable=None), {}, '[xyz](LanguageTable#cldf:l1)', 'xyz', None),
        ({}, {}, '[xyz](LanguageTable#cldf:l1)', 'The Language', None),
        ({}, {}, '[xyz](LanguageTable?_anchor=abc#cldf:l1)', '#abc', None),
        ({}, {}, '[xyz](LanguageTable?ids=l1,l2,l3#cldf:__all__)', ' and ', None),
        ({}, {}, '[xyz](ExampleTable#cldf:s1)', 'A sentence', None),
        ({}, {}, '[xyz](ExampleTable?as_link#cldf:s1)', 'href=', None),
        ({}, {}, '[xyz](ExampleTable?ids=s1#cldf:__all__)', '', None),
        ({}, {}, '[xyz](NopeTable#cldf:1)', 'NopeTable', None),
        (
            {},
            {},
            '[](Source#cldf:Meier2012)\n[](Source?cited_only#cldf:__all__)',
            'Meier',
            'Mueller'),
        ({}, {}, '[xyz](http://example.org)', 'http://example.org', None),
    ]
)
def test_markdown(model_map, renderer_map, md, substring, notsubstring, dbsession, req_factory):
    res = markdown(
        req_factory(dict(model_map=model_map, renderer_map=renderer_map)), md, session=dbsession)
    assert substring in res
    if notsubstring:
        assert notsubstring not in res
