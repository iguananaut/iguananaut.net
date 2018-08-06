A DLL Data Import Mystery
=========================

:author: Erik M. Bray
:date: 2018-08-03
:category: programming
:tags: c, windows, dlls, compilers, debugging
:slug: windows-data-import
:sumamry: What's going on when you import data from other DLLs, and why
          can't your C code reference that data in contexts where you might
          ordinarily be able to on Linux?


I've been working hard over the years to get CPython better supported on
Cygwin.  For years, the CPython code base has supported Cygwin off-and-on,
but it has not been "supported" in many years in the sense of having a
working build bot, or support from any of the CPython core developers.
That's a whole other story; but this is about just one relatively minor
compile-time bug I've seen come up `multiple
<https://bugs.python.org/issue21124>`_ `times
<https://bugs.python.org/issue34211>`_ in this porting effort.


The problem
^^^^^^^^^^^
To demonstrate the problem we don't need anything as complex as CPython.
In short, the problem arises in the case where we have a shared library, and
some other executable (either a program or another shared lib) that
references some data in the first library (and *specifically* data, as
opposed to functions).  In particular, the problem occurs when referencing
the external data in the initializer of some static struct, as in this
``main.c``:

.. code-block:: c

    #include <stdio.h>
    #include "ext_lib.h"


    static mystruct bar = {
        &foo,
        0xfdfdfdfd
    };


    int main(void) {
        printf("bar.a: %p\nbar.b: %d\n", bar.a, bar.b);
        return 0;
    }


where ``ext_lib.h`` contains the following definitions:

.. code-block:: c

    #if defined(__CYGWIN__) || defined(_WIN32)
        #ifdef DLLEXPORT
            #define DATA(RTYPE) extern __declspec(dllexport) RTYPE
        #else
            #define DATA(RTYPE) extern __declspec(dllimport) RTYPE
        #endif
    #else
        #define DATA(RTYPE) extern RTYPE
    #endif


    typedef struct _mystruct {
        int *a;
        int b;
    } mystruct;


    DATA(int) foo;


.. note::

    If you're puzzled by the above definition of the ``DATA`` macro, this
    has to do with proper handling of the ``__declspec(dllexport)`` and
    ``__declspec(dllimport)`` storage classes on Windows.  For a review of
    this, and in general of how data and function imports work in Windows
    see `Everything You Never Wanted to Know About DLLs
    <http://blog.omega-prime.co.uk/2011/07/04/everything-you-never-wanted-to-know-about-dlls/>`_.


The mystery is that the above code compiles *just fine* on Linux::

    gcc -c main.c -o main.o

However, on Windows (I am using Cygwin, but the same problem can be
reproduced using MSVC)::

    $ gcc -c main.c -o main.o
    main.c:6:5: error: initializer element is not constant
         &foo,
         ^
    main.c:6:5: note: (near initialization for ‘bar.a’)

I have known for some time that this related somehow to how DLL data imports
work, and the use of ``__declspec(dllimport)``, but I admit that I have
struggled to articulate *exactly* why this is happening on Windows, and why
the error occurs at *compile time* as opposed to link time.  For a spell I
thought it might even be a bug in gcc, until I was able to demonstrate the
same behavior in MSVC::

    >cl -c main.c
    Microsoft (R) C/C++ Optimizing Compiler Version 19.00.24213.1 for x64
    Copyright (C) Microsoft Corporation.  All rights reserved.

    main.c
    main.c(5): error C2099: initializer is not a constant


Constant expressions and rules lawyering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Taking a step back a bit, let's look at what this error message,
"initializer element is not constant", actually means.  I spent a while
googling this, and while there *is* a clear and simple answer, that answer
doesn't immediately obviously apply to the case at hand.

This error relates to limitations in the C standard as to what is allowed
when intializing some struct or other file-level variables.  Specifically,
going off the C99 standard, section 6.7.8 constraint 4:

    All the expressions in an initializer for an object that has static
    storage duration shall be constant expressions or string literals.

For example, the following is not allowed by the C standard at the file
level:

.. code-block:: c

    const int N = 1;
    int *M = N;

Even though ``N`` is declared ``const``, ``N`` by itself is pretty clearly
(I think) not a constant expression from the C compiler's perspective (C++
will allow it, however, due to its advanced compile-time execution
capabilities).

Okay, but what *exactly* constitutes a "constant expression"?  In fact,
there's a whole section on that--section 6.6.  In general it's what you'd
expect, such as an integer expression with a constant value that can be
determined at compile time.  There are some more advanced cases, however,
such as:

    | More latitude is permitted for constant expressions in initializers.
    | Such a constant expression shall be, or evaluate to, one of the
    | following:
    | 
    | — an arithmetic constant expression,
    | — a null pointer constant,
    | — an address constant, or
    | — an address constant for an object type plus or minus an integer
    |   constant expression.

Okay, so our ``&foo`` looks like it could be interpreted as an address
constant--it is an address after all.  But we should also check exactly what
is meant by "address constant":

    An *address constant* is a null pointer, a pointer to an lvalue
    designating an object of static storage duration, or a pointer to a
    function designator; it shall be created explicitly using the unary
    ``&`` operator or an integer constant cast to pointer type, or
    implicitly by the use of an expression of array or function type.

So we then need to ask, does ``foo`` have static storage duration?  The
short answer, generally, is "yes".  But we need to think about why that is
apparently considered *not* the case in the very Windows-specific case of
a data object declared ``extern __declspec(dllimport)``.


Link time relocations and extern data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It makes sense that the C standard explicitly writes "static storage
duration" when defining what it means by an "address constant".  From the
PoV of the C compiler it is mostly concerned just with a single translation
unit (TU)--i.e. a single ``.c`` source file.  If we had some
static-declared variable like:

.. code-block:: c

    static int foo = 0x55555555;

the compiler would reserve a space for this data in the ``.data`` section of
the object file, which has a fixed location--or address--within the file.
So when we then define ``bar = {&foo, ...}``, the compiler can also place
bar's data in the ``.data`` section, filling it in with the absolute
address of ``foo``, and so on.

Of course, that is the most naïve point of view--things more complicated
when we consider linking multiple object files, or runtime relocations due
to the fact that our code is not necessarily loaded at a fixed virtual
memory address.  Nevertheless, the compiler has some intelligence as to what
will happen.  In fact, it will leave the exact value of ``bar.a`` empty for
now, and include a relocation entry for the linker to fill in later, as it
may combine one or more TUs and their respective ``.data``, ``.text``, and
other sections and things will get moved around.  This is an implementation
detail at the level of binary object files, with which the C standard is
mostly unconcerned.

Link-time relocations can be quite sophisticated, and can put almost
anything almost anywhere in the file.  We can easily relocate data in the
``.data`` section of the file.  For example, after recompiling ``main.c``
(on Linux) with the above ``static`` redefinition of ``foo``::

    $ objdump -r -j .data main.o

    main.o:     file format elf64-x86-64

    RELOCATION RECORDS FOR [.data]:
    OFFSET           TYPE              VALUE
    0000000000000010 R_X86_64_64       .data

This says, take 64 bits from the value of ``.data`` and put them at offset
``0x10`` within the ``.data`` section.  Whereas the value ``.data`` refers
to the address of the ``.data`` section itself.  Looking at the contents of
the ``.data`` section we can clearly see that the value of our ``foo`` is
the first thing there::

    $ objdump -s -j .data main.o

    main.o:     file format elf64-x86-64

    Contents of section .data:
     0000 55555555 00000000 00000000 00000000  UUUU............
     0010 00000000 00000000 ffffffff 00000000  ................

When we pass this through the linker, things might get moved around a bit,
but not so much if we just pass in this single TU.  After running ``gcc
main.o -o main`` we see::

    $ objdump -s -j .data main

    main:     file format elf64-x86-64

    Contents of section .data:
     601030 00000000 00000000 00000000 00000000  ................
     601040 55555555 00000000 00000000 00000000  UUUU............
     601050 40106000 00000000 ffffffff 00000000  @.`.............

So some things *did* get moved around a bit, but we can see ``0x55555555``,
the value of our ``foo`` at the offset ``0x00601040``, and just below it
is the value of our ``bar`` with ``0x00601040``, the address of ``foo``,
filled in as a constant.  So after linking this was still effectively a
constant address, and the compiler understand this will be the case.


Run time dynamic relocation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

What if we go back to our original code, where on Linux we declared ``foo``
as an ``extern int foo``?  In fact on Linux, GCC will let us get away with
this for I think a few reasons.  First of all, ``extern`` essentially just
means that ``foo`` is defined in another TU, so it will have to be resolved
somehow by the linker.  After re-compiling ``main.c`` the resulting object
file looks almost the same, though the relocation records for ``.data`` look
slightly different::

    $ objdump -r -j .data main.o

    main.o:     file format elf64-x86-64

    RELOCATION RECORDS FOR [.data]:
    OFFSET           TYPE              VALUE
    0000000000000010 R_X86_64_64       foo

The symbol "foo" is undefined in this object file; it will be up to the
linker to resolve "foo" from some other object file, and fill its final
address in to the ``.data`` section.

Indeed, the original problem does have to do with the
``__declspec(dllimport)`` in the declaration of ``foo``.  If we change the
``DATA(int) foo;`` in ``ext_lib.h`` to just ``extern int foo;`` it will
compile just fine on Windows too, with the expectation that "foo" will be
resolved at link time.

But what if "foo" isn't resolved at link time?  On Linux this is technically
no always a problem, though for programs all symbols do require to be
resolved at link time so we pass ``-lext_lib`` to ``gcc``.  However, now
``foo`` comes from a shared library, whose runtime address *cannot* be known
ahead of time by the executable.  So we still need some way of resolving the
address of ``foo`` at run time.  One way, which is used here, is to create
an entry for it as a dynamic relocation entry, which is explained in more
detail in `Load-time relocation of shared libraries
<https://eli.thegreenplace.net/2011/08/25/load-time-relocation-of-shared-libraries>`_.

Again, on Linux, after linking main (after also compiling ``ext_lib``, which
just contains the definition of ``foo``) with::

    $ gcc -L. main.o -lext_lib -o main

the resulting executable contains a dynamic relocation table which includes
an entry for ``foo``::

    $ objdump -R main

    main:     file format elf64-x86-64

    DYNAMIC RELOCATION RECORDS
    OFFSET           TYPE              VALUE
    0000000000600ff8 R_X86_64_GLOB_DAT  __gmon_start__
    0000000000601050 R_X86_64_64       foo
    0000000000601018 R_X86_64_JUMP_SLOT  printf
    0000000000601020 R_X86_64_JUMP_SLOT  __libc_start_main
    0000000000601028 R_X86_64_JUMP_SLOT  __gmon_start__

This record indicates that the address of ``foo``, once known by the loader,
should be filled in at the offset ``0x00601050``, which just as before
happens to the location of ``bar`` within the ``.data`` section of the
image.  We can confirm this running the program under gdb::

    (gdb) x/g 0x00601050
    0x601050 <bar>: 0x00007ffff7dd9030
    (gdb) x/w 0x00007ffff7dd9030
    0x7ffff7dd9030 <foo>:   0x55555555

We can see that because the loader allows relocations in the ``.data``
section, because this all happens before the program begins running, from
the program's perspective ``bar`` is correctly initialized at start-up as
required, even though ``foo`` happens to be in a shared library.

This works because the ELF binary loader allows for dynamic relocations just
about as sophisticated as at link time.  Unfortunately, this is not so on
Windows.  The way PE/COFF files work, and hence the way Windows' dynamic
loader works, is that there exists an Import Address Table (IAT), explained
`here <https://msdn.microsoft.com/en-us/magazine/bb985992.aspx>`_ among a
few other resources.  The table contains just one entry for each "imported"
object (functions and data declared with ``__declspec(dllimport)``.  At
runtime this table is filled in with the addresses of each symbol as the
DLLs they live in are loaded.  You can also see, in the assembly, that
references to the symbol ``foo`` are replaced in the source with
``__imp_foo``, where ``__imp_foo`` refers to the IAT entry for ``foo``.

To demonstrate this, first we need to write some code that can actually be
compiled on Windows.  The workaround to this entire problem is, fortunately,
reasonably simple--just replace the ``&foo`` with ``NULL``, and finish
initializing ``bar`` at runtime:

.. code-block:: c

    static mystruct bar = {
        NULL,
        0
    };


    int main(void) {
        if (bar.a == NULL)
            bar.a = &foo;

        printf("bar.a: %p\nbar.b: %d\n", bar.a, bar.b);
        return 0;
    }

Looking at the assembly with ``objdump -dzr main.o`` shows::

    0000000000000000 <main>:
       0:   55                      push   %rbp
       1:   48 89 e5                mov    %rsp,%rbp
       4:   48 83 ec 20             sub    $0x20,%rsp
       8:   e8 00 00 00 00          callq  d <main+0xd>
                            9: R_X86_64_PC32        __main
       d:   48 8b 05 00 00 00 00    mov    0x0(%rip),%rax        # 14 <main+0x14>
                            10: R_X86_64_PC32       .bss
      14:   48 85 c0                test   %rax,%rax
      17:   75 0e                   jne    27 <main+0x27>
      19:   48 8b 05 00 00 00 00    mov    0x0(%rip),%rax        # 20 <main+0x20>
                            1c: R_X86_64_PC32       __imp_foo
      20:   48 89 05 00 00 00 00    mov    %rax,0x0(%rip)        # 27 <main+0x27>
                            23: R_X86_64_PC32       .bss
      27:   8b 15 08 00 00 00       mov    0x8(%rip),%edx        # 35 <main+0x35>
                            29: R_X86_64_PC32       .bss
      2d:   48 8b 05 00 00 00 00    mov    0x0(%rip),%rax        # 34 <main+0x34>
                            30: R_X86_64_PC32       .bss
      34:   41 89 d0                mov    %edx,%r8d
      37:   48 89 c2                mov    %rax,%rdx
      3a:   48 8d 0d 00 00 00 00    lea    0x0(%rip),%rcx        # 41 <main+0x41>
                            3d: R_X86_64_PC32       .rdata
      41:   e8 00 00 00 00          callq  46 <main+0x46>
                            42: R_X86_64_PC32       printf
      46:   b8 00 00 00 00          mov    $0x0,%eax
      4b:   48 83 c4 20             add    $0x20,%rsp
      4f:   5d                      pop    %rbp
      50:   c3                      retq

The important bit is the instruction at offset ``0x19``.  Here we can see
there's an IP-relative (as this is 64-bit Windows) load from some address
for which we have a relocation for the symbol ``__imp_foo`` (*not* just
``foo``).  We can see that ``bar``, now being uninitialized, is in ``.bss``
instead of ``.data``, but ``__imp_foo`` is somewhere else--but where?

Well we already said, ``__imp_foo`` is actually a reference to the IAT,
which lives in a different segment.  Again, we can see this especially
easily at runtime.  I noticed while playing around with this that there are
special symbols named ``__IAT_start__`` and ``__IAT_end__`` specifying
exactly where the IAT is in memory, and sure enough we can see that's where
``__imp_foo`` is::

    (gdb) info addr __imp_foo
    Symbol "__imp_foo" is at 0x100408170 in a file compiled without debugging.
    (gdb) info addr __IAT_start__
    Symbol "__IAT_start__" is at 0x1004080e8 in a file compiled without debugging.
    (gdb) info addr __IAT_end__
    Symbol "__IAT_end__" is at 0x100408180 in a file compiled without debugging.

``__imp_foo`` is at a fixed address relative to code that references it, so
the linker easily fixes up *those* relocations.  But because the IAT is
otherwise the only place where the loader fills the address of ``foo`` at
runtime, the loader cannot initialize static data with the address of
``foo``.

Conclusion
^^^^^^^^^^

TL;DR when loading Windows binaries we can't perform relocations in the
``.data`` section, so it's actually impossible to initialize objects with
static storage duration with data from an external DLL.  Initialization of
objects such as ``bar`` have to be completed after the fact at runtime and
there's just no good way around it.

Fortunately, both GCC and MSVC are smart enough to know that this will be
the case for variables declared with ``__declspec(dllimport)``.  It knows
that ``foo``--specifically ``__imp_foo``--effectively does not have static
storage duration, so its address cannot be used to initialize a struct.


Bonus: Why does it work for functions but not data?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

What if we took the original code, and changed the declaration of ``foo``
to a function, like:

.. code-block:: c

    DATA(int) foo(void)

(ignoring the fact that the ``DATA`` macro is now a misnomer; it still has
the same effect) and also update the definition of ``mystruct`` so that the
``mystruct.a`` member is a function pointer:

.. code-block:: c

    typedef struct _mystruct {
        int (*a)();
        int b;
    } mystruct;

Now recompile ``main.c`` and it works, even on Windows!  We can also see
that the relevant assembly (which reads from ``bar.a`` in order to pass it
to ``printf``) shows::

      2d:   48 8b 05 00 00 00 00    mov    0x0(%rip),%rax        # 34 <main+0x34>
                            30: R_X86_64_PC32       .data

So the object file actually references a relocation in ``.data`` (just as it
did on Linux when ``foo`` was a mere ``int``)::

    $ objdump -r -j .data main.o

    main.o:     file format pe-x86-64

    RELOCATION RECORDS FOR [.data]:
    OFFSET           TYPE              VALUE
    0000000000000000 R_X86_64_64       foo

No reference here to ``__imp_foo``.

At risk of vastly oversimplifying, for historical (?) reasons Windows
binaries contain symbols for all the function used in that particular
binary, even if they are imported from an external DLL.  Normally, when we
link an executable that uses code from a DLL, we pass the linker an "import
library" which contains stub definitions for all the functions in the
related DLL.  The stub function, which is included in the executable,
contains just a ``jmp`` to ``__imp_foo``.  And in fact, when we declare a
function with ``__declspec(dllimport)``, this allows the compiler to bypass
generating code like ``call foo``, and go straight to ``call __imp_foo``,
bypassing the stub function altogether.  But the stub function nevertheless
still exists.

In fact, we can see in the linked executable exactly what winds up in the
``.data`` section::

    main:     file format pei-x86-64

    Contents of section .data:
     100402000 00000000 00000000 00000000 00000000  ................
     100402010 40114000 01000000 00000000 00000000  @.@.............
     100402020 00000000 00000000 00000000 00000000  ................
     100402030 00000000 00000000 00000000 00000000  ................
     100402040 00000000 00000000 00000000 00000000  ................
     100402050 00000000 00000000 00000000 00000000  ................
     100402060 00000000 00000000                    ........

Although not immediately obvious, the value ``0x010041140`` at offset
``0x100402010`` is the address of the *stub function* for ``bar``.  From the
section headings we can see the offset off the ``.text`` section is at
``0x100401000``::

    Sections:
    Idx Name          Size      VMA               LMA               File off  Algn
      0 .text         000007c8  0000000100401000  0000000100401000  00000600  2**4
                      CONTENTS, ALLOC, LOAD, READONLY, CODE, DATA

And the symbol table shows the stub function at::

    [673](sec  1)(fl 0x00)(ty  20)(scl   2) (nx 0) 0x0000000000000140 foo

Add them together and you get ``0x0100401140``.  So what we see is that
``bar`` is initialized **not** with the actual address of the ``foo``
function, but with the address of its *stub function*.  This is assumed to
be good enough since the calling ``foo.a`` as a function will still
ultimately jump to the real function, and should work fine for most other
purposes as well, but it could be a little surprising and misleading,
especially while debugging.
