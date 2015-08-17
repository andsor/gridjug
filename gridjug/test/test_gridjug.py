# coding: utf-8

import inspect
import os
import shutil
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


@pytest.yield_fixture
def jugdir():
    with tempfile.TemporaryDirectory() as ret:
        yield ret


def test_execute():
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE)


def test_execute_jugdir():
    shutil.rmtree(PRIMES_JUGDIR, ignore_errors=True)
    assert not os.path.isdir(PRIMES_JUGDIR)
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE)
    assert os.path.isdir(PRIMES_JUGDIR)


def test_execute_specify_jugdir(jugdir):
    assert os.path.isdir(jugdir)
    assert not os.listdir(jugdir)  # empty directory
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    assert os.listdir(jugdir)  # non-empty directory


def test_init_jugspace(jugdir):
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)


def test_access_results(jugdir):
    gridjug.grid_jug(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    _, jugspace = jug.init(jugfile=PRIMES_JUGFILE, jugdir=jugdir)
    assert jug.value(jugspace['primes10']) == [
        True, True, False, True, False, True, False, False, False
    ]
