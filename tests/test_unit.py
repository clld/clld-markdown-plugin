from clld_markdown_plugin import *


def test_markdown_exc(mocker, dbsession, req):
    includeme(mocker.Mock(registry=mocker.Mock(
        settings=dict(
            clld_markdown_plugin=dict(
                model_map=dict(LanguageTable=mocker.Mock))))))
    res = markdown(req, '[xyz](LanguageTable#cldf:l1)', session=dbsession)
    assert res == '<p>xyz</p>'


def test_markdown_1(dbsession, req, default_config):
    res = markdown(req, '[xyz](LanguageTable#cldf:l1)', session=dbsession)
    assert 'The Language' in res


def test_markdown_2(dbsession, req, default_config):
    res = markdown(req, '[xyz](LanguageTable?ids=l1,l2,l3#cldf:__all__)', session=dbsession)
    assert ' and ' in res
