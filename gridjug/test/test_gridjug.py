# coding: utf-8

import inspect
import os
import shutil

import gridjug
import jug
import pytest

try:
    from tempfile import TemporaryDirectory  # Python >= 3.2
except ImportError:  # Python < 3.2
    # http://stackoverflow.com/a/19299884/2366781
    from _tempfile import TemporaryDirectory


# http://stackoverflow.com/a/50905/2366781
THIS_DIR = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
PRIMES_JUGFILE = os.path.join(THIS_DIR, 'primes.py')
PRIMES_JUGDIR = os.path.join(THIS_DIR, 'primes.jugdata')

# Determine whether we are on NLD clusters
ON_NLD_CLUSTER = (os.environ.get('SGE_CLUSTER_NAME', None) == 'NLD')
ON_NLD_LOGIN = ON_NLD_CLUSTER and (
    os.environ.get('CLUSTERNAME', None) == 'login'
)

NLD_GRIDMAP_PARAMS = {
    'queue': 'frigg.q,skadi.q,navier.q',
}


@pytest.yield_fixture
def jugdir():
    with TemporaryDirectory() as ret:
        yield ret


def test_execute():
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, local=True)


def test_execute_jugdir():
    shutil.rmtree(PRIMES_JUGDIR, ignore_errors=True)
    assert not os.path.isdir(PRIMES_JUGDIR)
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, local=True)
    assert os.path.isdir(PRIMES_JUGDIR)


def test_execute_specify_jugdir(jugdir):
    assert os.path.isdir(jugdir)
    assert not os.listdir(jugdir)  # empty directory
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir, local=True)
    assert os.listdir(jugdir)  # non-empty directory


def test_init_jugspace(jugdir):
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir, local=True)
    jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)


def test_access_results(jugdir):
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir, local=True)
    _, jugspace = jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    assert jug.value(jugspace['primes10']) == [
        True, True, False, True, False, True, False, False, False
    ]


@pytest.mark.skipif(not ON_NLD_LOGIN)
def test_nld_execute():
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, local=False)
