import types

import pytest

from clld_markdown_plugin import includeme


@pytest.fixture
def default_config():
    includeme(None)


@pytest.fixture
def req():
    return types.SimpleNamespace(route_url=lambda *args, **kw: '/p')


@pytest.fixture(scope='session')
def dbsession():
    import sqlalchemy as sa
    from clld.db.models import common
    from clld.db.meta import Base, DBSession

    engine = sa.create_engine('sqlite://')
    Base.metadata.create_all(bind=engine)
    DBSession.configure(bind=engine, expire_on_commit=False)
    DBSession.add(common.Language(id='l1', name='The Language'))
    DBSession.add(common.Language(id='l2', name='Language 2'))
    DBSession.add(common.Language(id='l3', name='Language 3'))
    DBSession.flush()
    yield DBSession
    DBSession.close()
    DBSession.remove()
