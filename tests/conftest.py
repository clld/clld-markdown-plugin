import types

import pytest
import sqlalchemy as sa
from clld.db.models import common
from clld.db.meta import Base, DBSession

from clld_markdown_plugin import includeme


@pytest.fixture
def req_factory():
    def req(settings=None):
        config = includeme(types.SimpleNamespace(
            registry=types.SimpleNamespace(settings={'clld_markdown_plugin': settings or {}})))

        return types.SimpleNamespace(
            registry=config.registry,
            route_url=lambda *args, **kw: '/p{}'.format(
                '#' + kw['_anchor'] if kw.get('_anchor') else ''))
    return req


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
    DBSession.add(common.Source(id='Meier2012', name="Meier"))
    DBSession.add(common.Source(id='Mueller2012', name="Mueller"))
    DBSession.flush()
    yield DBSession
    DBSession.close()
    DBSession.remove()
