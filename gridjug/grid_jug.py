# coding: utf-8

from __future__ import absolute_import, division, print_function

import io

try:  # Python >= 3.4
    from contextlib import redirect_stdout
except ImportError:
    # Credit: J.F. Sebastian http://stackoverflow.com/a/22434262/2366781
    import sys
    from contextlib import contextmanager

    @contextmanager
    def redirect_stdout(new_target):
        # replace sys.stdout
        old_target, sys.stdout = sys.stdout, new_target
        try:
            # run some code with the replaced stdout
            yield new_target
        finally:
            # restore to the previous value
            sys.stdout = old_target


def grid_jug(
    jugfile,
    jugdir=None,
    jug_args=None,
    jug_nworkers=4,
    name='gridjug',
    keep_going=False,
    verbose=False,
    capture_jug_stdout=False,
    **kwargs
):
    """
    A light-weight wrapper to run Jug with GridMap on a Grid Engine cluster

    From their own description, GridMap is a package that allows to easily
    create jobs on a Grid Engine powered cluster directly from Python.
    This wrapper lets GridMap simply spawn several jug-execute workers on a
    Grid Engine cluster.
    Thus we have the benefit of programmatic (reproducible) execution of Jug
    processes.
    Furthermore, GridMap adds a convenient monitoring and reporting layer.
    Under the hood, of course, Jug keeps doing the actual work.

    Parameters
    ----------
    jugfile : path
        Path to the jugfile

    jugdir : path
        Where to save intermediate results

    jug_args : list
        Other jug command-line arguments.
        Note that ``'execute'`` is already included.
        The command line is roughly equivalent to:

            'jug execute {jugfile} ' + ' '.join(jug_args)

    jug_nworkers : int, optional
        number of Grid Engine tasks to start
        (i.e. number of times 'jug execute' is run)

    name : str, optional
        base name of the Grid Engine task

    keep_going : bool, optional
        Strongly recommended! Defaults to ``False``: if a single Jug task
        fails, GridMap will cancel all jobs!
        If ``True``, Jug does not raise an exception but keeps retrying the
        task.

    verbose : bool, optional
        If ``True``, Jug logs ``INFO`` events

    capture_jug_stdout : bool, optional
        Defaults to ``False``.
        If ``True``, captures Jug's task summary printed to stdout.

    **kwargs : keyword-dict, optional
        additional options passed through to :any:`gridmap.grid_map`

    See Also
    --------

    :any:`gridmap.grid_map` : The map function

    `Jug subcommands <http://jug.readthedocs.org/en/latest/subcommands.html>`_

    """

    import gridmap

    jug_argv = ['jug', 'execute']
    jug_argv.append('{}'.format(jugfile))
    if jugdir is not None:
        jug_argv.append('--jugdir={}'.format(jugdir))
    if keep_going:
        jug_argv.append('--keep-going')
    if verbose:
        jug_argv.append('--verbose=INFO')
    if jug_args is not None:
        jug_argv.extend(jug_args)

    # function arguments for grid_map
    # note that there are multiple lists here
    # the innermost list is the list of arguments to jug
    # this needs to stay a list as jug.main accepts a single argument argv
    # which is a list of parameters for jug
    # https://github.com/luispedro/jug/blob/15a7043f6f859810b5e6af1638176d1a9cb70f5a/jug/jug.py#L405
    #
    # we wrap this inner list in a wrapper list [jug_argv] that gridmap
    # "expands" to its single item jug_argv upon calling the jug.main function,
    # with that very single item jug_argv as the single argument
    # https://github.com/pygridtools/gridmap/blob/master/gridmap/job.py#L225
    #
    # finally, the wrapper list [jug_arvg] is contained in the outer list
    # [[jug_argv]]. The outer list is multiplied by the number of workers to
    # create an outer list of that many items, each of which is the wrapped
    # list [jug_argv] to supplied to each of the worker jobs
    # https://github.com/pygridtools/gridmap/blob/master/gridmap/job.py#L929
    # https://github.com/pygridtools/gridmap/blob/master/gridmap/job.py#L933
    #
    args_list = jug_nworkers * [[capture_jug_stdout, jug_argv]]

    return gridmap.grid_map(
        f=_jug_main,
        args_list=args_list,
        name=name,
        **kwargs
    )


def _jug_main(capture_stdout, *args, **kwargs):
    """
    wrapper function for pickle
    """
    import jug

    if capture_stdout:
        f = io.StringIO()
        with redirect_stdout(f):
            ret = jug.jug.main(*args, **kwargs)
    else:
        ret = jug.jug.main(*args, **kwargs)

    return ret
