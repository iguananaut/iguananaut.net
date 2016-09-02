On Python, Polynomials, and Parsers (part 1)
============================================

:author: Erik M. Bray
:date: 2016-09-02
:category: programming
:tags: python, sage, debugging
:slug: python-polynomials-parsers-1
:sumamry: I describe an problem I had that let me down a rabbit hole
          in CPython, and musings about stack-based limitations
          therein.

.. note::

    Most of this series doesn't really have anything to do with parsers per se,
    and more do with analysis of abstract syntax trees (ASTs) which are the output
    of a parser.  I just couldn't resist the alliteration.


The initial problem
^^^^^^^^^^^^^^^^^^^

One of my current major tasks to is port the `SageMath
<http://www.sagemath.org/>`_ mathematical software toolkit to work on Windows.
This turns out to be a surprisingly challenging task—SageMath has a large
number of dependencies, some of which make platform-specific assumptions and
don't support Windows. Currently I am dependent on Cygwin for this—I hope to
break away from Cygwin dependence eventually, but that's beside the point.

While running Sage's massive test suite of tens of thousands of tests, I
encountered one test—which involves computing someting I don't understand about
isogenies of `elliptic curves <https://en.wikipedia.org/wiki/Elliptic_curve>`_
—which was resulting in a segmentation fault (only on Windows). I am not a
mathematician, and do not understand the majority of the math in SageMath (and
neither do the mathematicians who work on it—it's too huge for any one person
to understand all of). In particular, while I've used Sage solve some basic
analytical problems, most of its complex hierarchies of algebraic objects and
operations thereon are beyond me. I know what an elliptic curve is but I don't
know much about what you do with them. So a segfault deep in some calculation
about a property of an elliptic curve was a bit intimidating.


Debugging
^^^^^^^^^

The good news was being a platform-specific segfault there was a chance the
problem had nothing to do with details of the calculation itself, and that
suspicion bore out. As usual when there's a bug in Python, I started by
stepping through the failing test with `pdb
<https://docs.python.org/3/library/pdb.html>`_. This led me into a function
called `Psi2
<https://git.sagemath.org/sage.git/tree/src/sage/schemes/elliptic_curves/isogeny_small_degree.py?id=00722fdd62ec1eea787ae97eec986888cd2d9601#n1446>`_,
which was being called with an input of 71. It tured out to be the last line of
this function that was causing the segfault. SO I was able to isolate the
problem to this function:

.. code-block:: python

    >>> from sage.schemes.elliptic_curves.isogeny_small_degree import Psi2
    >>> Psi2(71)
    Segmentation fault (core dumped)

Because large swaths of Sage are written in `Cython <http://cython.org/>`_, the
Python debugger is not particularly useful beyond this point. And in any case
because we're getting a segmentation fault, the problem has to be below the
Python level anyways. I was mostly expecting the problem to be in one of Sage's
many dependencies, such as the `Singular <https://www.singular.uni-kl.de/>`_
system, which is used for many computations about polynomials. So the next step
is to put the failing code in a short script, and run Python through gdb, which
can catch the segmentation fault and provide a C-level traceback::

    (gdb) run Psi2.py
    ... various noise, like new threads spawning (Cygwin uses lots of threads to implement things like signal handling) ...
    Program received signal SIGSEGV, Segmentation fault.
    0x00000003f42f32ad in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll

Huh! That was not what I was expecting—a segfault somewhere in the bowels of
the Python interpreter itself. Not that it's the first time I've ever found a
segfault in the Python interpreter, but not what I was expecting for this code.
I wasn't using a debug build of Python, so I don't get much in the way of
debugging info other than the function name. But let's look at the rest of the
backtrace to see if we can tell something more::

    (gdb) bt
    #0  0x00000003f42f32ad in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #1  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #2  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #3  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #4  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #5  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #6  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #8  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #9  0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #10 0x00000003f42f32b2 in symtable_visit_expr () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    ...

... and so on for another 40 lines. Yikes! Looks like a recursion bug. In fact::

    (gdb) bt -10
    #7174 0x00000003f42bbec8 in call_function () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7175 0x00000003f42b66c7 in PyEval_EvalFrameEx () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7176 0x00000003f42b9158 in PyEval_EvalCodeEx () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7177 0x00000003f42aee74 in PyEval_EvalCode () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7178 0x00000003f42ebf6a in run_mod () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7179 0x00000003f42ebeee in PyRun_FileExFlags () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7180 0x00000003f42ea5bd in PyRun_SimpleFileExFlags () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7181 0x00000003f42e9bcb in PyRun_AnyFileExFlags () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7182 0x00000003f43062bc in Py_Main () from /home/embray/src/sagemath/sage-cygwin/local/bin/libpython2.7.dll
    #7183 0x0000000100401103 in main (argc=2, argv=0xffffcc00) at ./Modules/python.c:23

A good 7000+ stack frames worth of recursion. The reason for the segfault is
clear then —a good ol' stack overflow!

This also explains why this test failed on Windows, but not other platforms
(most Sage developers are using some \*nix variant). Programs run with a default
limit on their stack size, usually provided by the operating system. On most
Linux systems, for example, this is 8 MB. On Windows the the OS is still
responsible for reserving the stack, but executables can actually have their
requested stack size compiled into them at link time. By default (at least in
Cygwin's GCC) this is just 1 MB. So clearly this could fail just as well on
Linux with a smaller stack—and indeed when I tried setting::

    $ ulimit -s 1024

to set my stack limit to 1 MB, I got the same crash on Linux.

In the next post I'll explain in a little more detail what the problematic code
in Sage is doing, and why it's crashing Python somewhere in its symbol table
analysis. Then I'll write a post exploring this particular corner of the
CPython interpeter. While I've spent a good amount of time in CPython's code,
the compiler is one area where I had previously spent very little time, so it
was an interesting learning experience.
