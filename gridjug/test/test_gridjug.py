# coding: utf-8

import inspect
import os
import tempfile

import gridjug
import jug
import pytest

# http://stackoverflow.com/a/50905/2366781
THIS_DIR = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
PRIMES_JUGFILE = os.path.join(THIS_DIR, 'primes.py')
PRIMES_JUGDIR = os.path.join(THIS_DIR, 'primes.jugdata')

FAILING_JUGFILE = os.path.join(THIS_DIR, 'failing.py')

# Determine whether we are on NLD clusters
ON_NLD_CLUSTER = (os.environ.get('SGE_CLUSTER_NAME', None) == 'NLD')
ON_NLD_LOGIN = ON_NLD_CLUSTER and (
    os.environ.get('CLUSTERNAME', None) == 'login'
)

TEMP_DIR = None
if ON_NLD_LOGIN:
    TEMP_DIR = os.path.join(THIS_DIR, 'tmp')
    if not os.path.isdir(TEMP_DIR):
        os.mkdir(TEMP_DIR)

NLD_GRIDMAP_PARAMS = {
    'local': False,
    'require_cluster': True,
    'temp_dir': TEMP_DIR,
    'quiet': False,
    'queue': 'frigg.q,skadi.q',
    'interpreting_shell': '/bin/bash',
    'copy_env': False,
}


def test_execute():
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, local=True)


def test_execute_jugdir():
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, local=True)
    assert os.path.isdir(PRIMES_JUGDIR)


def test_execute_specify_jugdir(tmpdir):
    jugdir = tmpdir
    assert jugdir.ensure_dir()
    assert not jugdir.listdir()  # empty directory
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE, jugdir=jugdir.strpath, local=True,
    )
    assert jugdir.listdir()  # non-empty directory


def test_init_jugspace(tmpdir):
    jugdir = tmpdir
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE, jugdir=jugdir.strpath, local=True,
    )
    jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir.strpath)


def test_access_results(tmpdir):
    jugdir = tmpdir
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE, jugdir=jugdir.strpath, local=True,
    )
    _, jugspace = jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir.strpath)
    assert jug.value(jugspace['primes10']) == [
        True, True, False, True, False, True, False, False, False
    ]


def test_failing(tmpdir):
    jugdir = tmpdir
    res = gridjug.grid_jug(
        jugfile=FAILING_JUGFILE, jugdir=jugdir.strpath, local=True,
    )
    for result in res:
        assert isinstance(result, RuntimeError)


def test_failing_keep_going(tmpdir):
    jugdir = tmpdir
    gridjug.grid_jug(
        jugfile=FAILING_JUGFILE, jugdir=jugdir.strpath, local=True,
        keep_going=True,
    )
    _, jugspace = jug.init(jugfile=FAILING_JUGFILE, jugdir=jugdir.strpath)
    for n, task in zip(range(2, 11), jugspace['primes10']):
        assert task.can_load() == (n != 6)


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_execute():
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE,
        **NLD_GRIDMAP_PARAMS
    )


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_execute_jugdir():
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE,
        **NLD_GRIDMAP_PARAMS
    )
    assert os.path.isdir(PRIMES_JUGDIR)


@pytest.fixture
def jugdir():
    ret = tempfile.mkdtemp(suffix='.jugdata', dir=TEMP_DIR)
    assert os.path.isdir(ret)
    assert not os.listdir(ret)  # empty directory
    return ret


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_execute_specify_jugdir(jugdir):
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE,
        jugdir=jugdir,
        **NLD_GRIDMAP_PARAMS
    )
    assert os.listdir(jugdir)  # non-empty directory


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_init_jugspace(jugdir):
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE,
        jugdir=jugdir,
        **NLD_GRIDMAP_PARAMS
    )
    jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_access_results(jugdir):
    gridjug.grid_jug(
        jugfile=PRIMES_JUGFILE,
        jugdir=jugdir,
        **NLD_GRIDMAP_PARAMS
    )
    _, jugspace = jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    assert jug.value(jugspace['primes10']) == [
        True, True, False, True, False, True, False, False, False
    ]


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_failing(jugdir):
    with pytest.raises(RuntimeError):
        gridjug.grid_jug(
            jugfile=FAILING_JUGFILE,
            jugdir=jugdir,
            **NLD_GRIDMAP_PARAMS
        )


@pytest.mark.skipif(not ON_NLD_LOGIN, reason='Not on NLD cluster login node')
def test_nld_failing_keep_going(jugdir):
    gridjug.grid_jug(
        jugfile=FAILING_JUGFILE,
        jugdir=jugdir,
        keep_going=True,
        **NLD_GRIDMAP_PARAMS
    )
    _, jugspace = jug.init(jugfile=FAILING_JUGFILE, jugdir=jugdir)
    for n, task in zip(range(2, 11), jugspace['primes10']):
        assert task.can_load() == (n != 6)
