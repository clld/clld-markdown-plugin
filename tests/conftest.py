import types

import pytest
import sqlalchemy as sa
from clld.db.models import common
from clld.db.meta import Base, DBSession

from clld_markdown_plugin import includeme


@pytest.fixture
def default_config():
    includeme(None)


@pytest.fixture
def req():
    return types.SimpleNamespace(
        route_url=lambda *args, **kw: '/p{}'.format(
            '#' + kw['_anchor'] if kw.get('_anchor') else ''))


@pytest.fixture(scope='session')
def dbsession():
    engine = sa.create_engine('sqlite://')
    Base.metadata.create_all(bind=engine)
    DBSession.configure(bind=engine, expire_on_commit=False)
    l1 = common.Language(id='l1', name='The Language')
    DBSession.add(l1)
    DBSession.add(common.Language(id='l2', name='Language 2'))
    DBSession.add(common.Language(id='l3', name='Language 3'))
    DBSession.add(common.Sentence(id='s1', name="Ein Satz", description="A sentence", language=l1))
    DBSession.flush()
    yield DBSession
    DBSession.close()
    DBSession.remove()
