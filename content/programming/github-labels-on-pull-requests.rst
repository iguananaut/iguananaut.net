Adding Labels to GitHub Pull Requests
=====================================

:author: Erik M. Bray
:date: 2013-11-29
:category: programming
:tags: github, projects, userscripts
:slug: github-labels-on-pull-requests
:summary: Introducing a Greasemonkey script to add full label support to the GitHub pull request UI

One thing that I'm often down on GitHub about is its inferior issue tracking system.
I think that for many, if not the majority of smaller open source projects, that have minimal
product management, it's sufficient.  But for larger projects that I work on, namely `Astropy`_, its
limitations really become apparent.

In particular, what I miss from better issue trackers like Trac's or Bitbucket's is a greater wealth
of metadata that can be attached to an issue (let's not even get into workflows).  GitHub supports
a (single) assignee to an issue, a milestone, and any number of "labels".  Labels are fairly freeform
and can act as a stand-in for other metadata (affected versions, affected components, etc.) with
judicious use, and this is exacly what I *really* need for Astropy.  There may not be a specific
"Affected Version" metadata field, but I can at least create labels like "affects-0.2.x", meaning that
a particular bug affects the lastest 0.2.x release and should be included in the next bugfix release.
It's not pretty but at least it works.

But where labels *really* fall over in GitHub is that they aren't shown on *pull requests*.  At least
not in the most obvious context--on the page for the pull request (PR) itself.  To clarify, GitHub's data
model treats PRs more or less like a "subclass" of normal issues.  Every PR has an issue (with the same
number) associated with it, along with some pull request-specific data such as what comparison to make the
PR from, and its merge status.  So there's no reason PRs *can't* have labels--just add labels to the issue
associated with a PR.  In fact, it's entirely possible to do this through GitHub's API, and I believe some
command-line utilities such `Hub`_ might support this (though I haven't actually checked).  *In fact* you
can even turn a normal issue into a pull request by attaching the right metadata to it--I use
`this script <https://gist.github.com/eteq/1750715>`_ that `Erik Tollerud`_ hacked together to do this all
the time.

This use case--converting an issue to a PR--especially illustrates the problem.  Say you have an issue with
a bunch of labels attached to it, but then you use this script to attach some code to the issue.  Refresh
the page and suddenly: No more labels.  Nothing to distinguish the PR except for what milestone it's assigned
to.

That doesn't mean the labels ever went away.  In fact, you *can* still view them on the full list of issues
for the repository--the issue listing UI supports labels for normal issues and PRs alike.  It even supports
a batch editing mode which allows adding and removing issues from PRs.  So it's not like they never intended
it to be possible.  They for some reason just haven't gotten around to adding it to the UI for individual
issues.

So anyways, TL;DR: I wrote `this Greasemonkey script <http://userscripts.org/scripts/show/185095>`_ to
display and enable management of labels on pull requests.

The most obvious place for this would be in the same place they appear on normal issues--the right sidebar 
next to the PR description, under the merge status:

.. image:: https://raw.github.com/iguananaut/userscripts/master/github/labels_on_pull_requests/images/screenshot4.png
    :alt: GitHub pull request without labels
    :align: center
    
It was very simple to add the appropriate HTML right in this spot.  The end result looks something like
this:

.. image:: https://raw.github.com/iguananaut/userscripts/master/github/labels_on_pull_requests/images/screenshot3.png
    :alt: Pull request with labels
    :align: center
    
And it was no trouble to get the label selection menu working (it's just an HTML 5 form):

.. image:: https://raw.github.com/iguananaut/userscripts/master/github/labels_on_pull_requests/images/screenshot2.png
    :alt: Adding a label to a pull request
    :align: center


This was a fun little issue to work on, as my current work rarely affords me to do web frontend development
(which used to occupy a good half my time).  So my JavaScript is a little rusty and probably garbage.
The HTML for GitHub's label selection form is a bit hefty, and I started out just building up the same structure
with DOM methods.  But that got very cumbersome very fast, so I decided to try out one of the JavaScript-based
HTML template systems.  These had only just started to become useful around the time I stopped doing web
work, so I've never had the opportunity before.

I chose `Handlebars`_ for this purpose, mainly just because I had heard of it, so it was the first thing that
popped into mind when I thought "maybe I should use a template system".  I read the docs for it and found it
satisfying, so I went with it.

This, however, motivated my introduction to the relatively new world of `Content Security Protection`_ (CSP).
It turns out that Handlebars' template parsing requires being able to perform an ``eval()``, which CSP disallows
by default (GitHub would have to explicitly allow it in their CSP rules, and it's for the best that they
don't).  That said, part of the point of Greasemonkey and userscripts in general is that as a user I have
(supposedly) vetted the functionality of this script and have okay'd it to run on my system--in principle
CSP should only protect me from malicious scripts of which I did not authorize the execution.  But current
versions of Firefox, at least, remain overly aggressive in enforcing a site's CSP rules even for userscripts
executed on pages from that site.

Digging a little deeper, however, I found that Handlebars supports
pre-compilation of templates into executable code that does not require runtime
evals or anything of that nature.  It was easy enough, following the
instructions, to install Handlebars with node.js and run their script to
compile my template.  Then I just added the template to the GitHub repo for my
script and listed it as a prerequisite, after Handlebars itself.  That cleared
the whole thing up.

The only other challenge was colors:  GitHub is using some algorithm server-side to determine good font colors
to use in contrast with each label's color.  It would be very difficult to determine *exactly* what they're
doing, but with a bit of experimentation I was able to get it "close enough".

So far I've tested this only one Firefox 23 and Chrome 28 (with Tampermonkey) which happen to be the browsers
installed on my laptop at the moment.  So please let me know if it's successful (or unsuccessful) on other
browsers.


.. _Astropy: http://www.astropy.org/
.. _Hub: http://hub.github.com/
.. _Erik Tollerud: https://github.com/eteq
.. _Handlebars: http://handlebarsjs.com/
.. _Content Security Protection: http://en.wikipedia.org/wiki/Content_Security_Policy
