Adding Labels to GitHub Pull Requests
=====================================

:status: draft
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
a particular bug accets the lastest 0.2.x release and should be included in the next bugfix release.
It's not pretty but at least it works.

But where labels *really* fall over in GitHub is that they aren't shown on *pull requests*.  At least
not in the most obvious context--on the page for the pull request (PR) itself.  To clarify, GitHub's data
model treats PRs more or less like a "subclass" of normal issues.  Every PR has an issue (with the same
number) associated with it, along with some pull request-specific data such as what comparison to make the
PR from, and its merge status.  So there's no reason PRs *can't* have labels--just add labels to the issue
associated with a PR.  In fact, it's entirely possible to do this through GitHub's API, and I believe some
command-line utilities such `Hub`_ might support this (though I haven't actually checked).  *In fact* you
can even turn a normal issue into a pull request by attaching the right metadata to it--I use
`this script <https://gist.github.com/eteq/1750715>` that `Erik Tollerud`_ hacked together to do this all
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

The most obvious place for this would be in the same place they appear on normal issues--the right sidebar 
next to the PR description, under the merge status:




.. _Astropy: http://www.astropy.org/
.. _Hub: http://hub.github.com/
.. _Erik Tollerud: https://github.com/eteq
