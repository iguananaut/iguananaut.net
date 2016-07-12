Analyzing Git Repositories in Pandas
====================================

:author: Erik M. Bray
:date: 2014-01-03
:category: programming
:tags: git, pandas, python
:slug: git-logs-in-pandas
:summary: Although the git log command is extremely powerful for use in
          exploring a git repository's history, I found it easier to for some
          kinds of analysis to dump git log output into a Pandas_ DataFrame_

Although the git log command is extremely powerful for use in exploring a git
repository's history, I found that for some kinds of analysis it may be easier
to dump git log output into a Pandas DataFrame and work with it in Python.

In particular what motivated this was that I was trying to recreate the graph
of commit activity over time that GitHub shows on its "Contributors" graph
page.  For a large project `like Astropy
<https://github.com/astropy/astropy/graphs/contributors>`_ that looks something
like this:

.. image:: {filename}/static/images/git-logs-in-pandas/github-astropy-commits-graph.png
    :alt: Astropy commit activity over time
    :align: center

This graph is nice enough on its own for use in a web browser, but I wanted to
make my own replication of it using matplotlib for my own use.  There do exist
a number of software packages already that will generate statistics and plots
from git repositories.  I would link to some, but honestly I didn't bother even
trying any of them since the plots they made were damned ugly.  I figured I
only had a few limited use cases I was interested in so it would be easier to
do myself and probably look a little better.

My first attempt actually did take advantage of Pandas from the start.  This
was the first time I had really attempted to do much with Pandas for my own
use (aside from working on small tutorials to give to other people).  So one
thing I did know was that I was working with a time series and that Pandas
might include some tools that would make my life easier.  That said I am still
learning Pandas myself, and some of my solutions may be ugly and hacky.

I assumed, to start with, that I would sample the commit activity on a weekly
basis rather than daily.  ``git log`` supports ``--since`` and ``--until``
arguments that allow returning a sample of the log in a specific date range.
But I needed a quick, easy way to generate a list of dates separated by one
week.  I could have done this easily enough in pure Python using timedeltas,
but since I already had Pandas installed my first attempt used its built-in
``date_range`` function:

.. code:: python

    >>> from pandas import date_range
    >>> from pandas
    >>> date_range('2011-07-25', '2014-01-03', freq='W')
    <class 'pandas.tseries.index.DatetimeIndex'>
    [2011-07-31 00:00:00, ..., 2013-12-29 00:00:00]
    Length: 77, Freq: W-SUN, Timezone: None

As you can see, a "gotcha" in Pandas is that the ``'W'`` frequency for week
actually defaults to weeks beginning on Sunday.  A reasonable default, to be
sure, but this cuts off dates in my range before the first Sunday in the range.
There are a few possible workarounds for this, but for my case I just shifted
the start day to the first Sunday before the actual start day.  There is a
better way I later discovered to do this using the ``period_range`` function
but I will leave that as an exercise.

My full solution involved looping over the dates in my date range and making
repeated calls to ``git log``, a process with really more overhead than
necessary but it was fine for a first attempt:

.. code:: python

    from datetime import datetime
    from pandas import date_range
    import shlex
    import subprocess as sp

    # I just looked up and hard-coded the start date of the repository in
    # this version
    start = datetime(year=2011, month=7, day=24)
    end = datetime.today()
    rng = date_range(start, end, freq='W')

    # This will list each commit in the given range on one line each (excluding
    # merge commits).  This means I can count commits by simply counting lines
    # of output
    cmd = 'git log --oneline --since=%s --until=%s --no-merges'

    def count_commits(since, until):
        p = sp.Popen(shlex.split(cmd % (since, until)), stdout=sp.PIPE)
        p.wait()
        return len(p.stdout.readlines())

    commits_by_week = []
    for idx in xrange(len(rng) - 1):
        since = rng[idx]
        since_iso = since.date().isoformat()
        until_iso = rng[idx + 1].date().isoformat()
        commits_by_week.append((since, count_commits(since_iso, until_iso)))

    # Special case for the last week in the range
    since = rng[-1]
    since_iso = since.date().isoformat()
    until_iso = end.isoformat()
    commits_by_week.append((since, count_commits(since_iso, until_iso)))

I plopped this script directly into my git repository and ran it.  I've
ommitted that version of the plotting code, but it came out with something
like this (after taking a rather long time to make all those ``git log``
calls):

.. image:: {filename}/static/images/git-logs-in-pandas/first-attempt.png
    :alt: First attempt at a commit activity graph
    :align: center

If you compare that to the version from GitHub you can see that while there
are similar periods of activity and inactivity, the two plots look rather
different.  In particular, my version has several large spikes that are
absent from the GitHub version.  At first I thought I might try sampling by
day instead of week, but that only made the output even spikier, and all those
``git log`` calls were taking inordinately long.

After just a little further exploration of the GitHub graphs and comparison
with my actual git log I realized the major difference:  GitHub's time series
is using the "author date" of the commits rather than the "committer date" to
produce its graph.  All git commits actually carry (at least) two dates.  As
`this article <http://alexpeattie.com/blog/working-with-dates-in-git/>`_ by
Alex Peattie explains, the "author is the person who originally wrote the work,
whereas the committer is the person who last applied the work."  And further,
``git log`` "uses commit dates when given a ``--since`` option."  So my time
series was based on commit dates, rather than author dates.  That largely
explains the big spikes—it turns out they largely correspond to activity just
before making a release of Astropy, when many pull requests were being merged.
When the PRs are merged their commits get a commit date same as when they are
merged.

In fact, in general, the git log for a large project with many contributors is
very much *not* in chronological order of when the commits were first created.
Rather, because of the way git log works, the commits it lists will generally
be in topological order.  It starts by looking at your ``HEAD`` commit and then
just walking back through its parents.  This has nothing to do with the actual
chronological order in which the commits were written by their original
authors.

My first attempt at solving this problem was to use a ``git log`` command with
a custom format string returning only the author dates (as well as the hashes
though they aren't particularly needed)::

    git log --no-merges --date=short --pretty='format:%ad %H'

This displays the author dates fine, but they are still in topological order.
When trying to use this with ``--since`` and ``--until`` the returned commits
are still based in the commit dates and not somehow magically sorted and
grouped by author date.  I realized at this point that there was no way I
could rely git log to prepare the data in the way I wanted.  It makes much
more sense at this point to use Pandas.

In addition to making the code vastly simpler, it only required one call to
``git log`` and was much faster.  You can use a custom format with ``git log``
to produce any and all data you want from git in a tsv or csv format and
load it directly into a Pandas DataFrame.  For example, in addition to the
author date, I also wanted the author, and for the heck of it the hash:

.. code:: python

    import io
    from pandas import read_csv

    cmd = "git log --no-merges --date=short --pretty='format:%ad\t%H\t%aN'"
    p = sp.Popen(shlex.split(cmd), stdout=sp.PIPE)
    # p.wait() will likely just hang if the log is long enough because the
    # stdout buffer will fill up
    stdout, _ = p.communicate()

    table = read_csv(io.StringIO(stdout.decode('utf-8')), sep='\t',
                     names=['date', 'hash', 'author'], index_col=0,
                     parse_dates=True).sort()

The ``index_col=0`` and ``parse_dates=True`` indicate that the first column
('date') should be treated as the index for the table, and that its values
should be parsed as dates.  The ``.sort()`` call ensures that the returned
table is sorted in ascending order by date.

Now the commits are indexed by their author date, and for many applications
that would be fine.  But I still wanted to try grouping by weekly periods
for use in my plot instead.  There are probably many ways to do this, but the
one I settled on was to convert to a DataFrame indexed by periods instead of
dates:

.. code:: python

    table = table.to_period(freq='W')

Then it was easy to generate counts of commits in each period using a simple
combination of ``groupby`` and ``aggregate``:

.. code:: python

    commits_per_period = table.hash.groupby(level=0).aggregate(len)

I specically chose to aggregate over the hash column.  I could have just as
easily used author.  This gives me a table mapping periods to the number of
commits in each period.  I'm not sure if this next step is necessary, but
I could convert this to a list of datetimes and associate array of commit
counts for use with matplotlib:

.. code:: python

    dates = [p.start_time.date() for p in commits_per_period.index]
    ncommits = commits_per_period.values

The result looks like this:

.. image:: {filename}/static/images/git-logs-in-pandas/second-attempt.png
    :alt: Second attempt at a commit activity graph
    :align: center

It still has a few sharper spikes and other small differences from the GitHub
version, but I think is close enough now.  There could be small differences in
how they're sampling the data, and additional smoothing that I'm not doing.
It doesn't matter—this is still an accurate representation of the *actual*
activity of developers working on the project.

This is of course just scratching the surface.  With git commit histories
loaded into Pandas there's no end to the interesting analysis that could be
done.  For example, I later went on to add a plot of the number of committers
to the project over time.  That's still pretty basic though, and as I am not
a statistician I can only imagine the data one could pull out of a git repo in
this way.

The full code, along with the plotting code is here:
https://gist.github.com/iguananaut/8248063 with thanks to
`Olga Botvinnik <https://github.com/olgabot>`_ for providing prettier plots
with prettyplotlib_.

.. _Pandas: http://pandas.pydata.org/
.. _DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
.. _prettyplotlib: http://olgabot.github.io/prettyplotlib/
