# Zetanote

Yet another note service.

Usage:

```
$ git clone git@github.com:soasme/zetanote.git
$ cd zetanote
$ pipenv install -e .
$ pipenv shell
# mkdir data
# export ZETANOTE_DATA=./data
# export ZETANOTE_USER=$USER
# zeta open ##### Will prompt default $EDITOR. See below on how to write a note.
# zeta ls
```

The note content includes meta and note text.
Note meta is formed line by line in format like `key: value`.
Especially, the meta field `key` is essential, which is basically used as note identity.
An empty line needs to be inserted between note meta and note text.

Below is an example note:

```
key: 2244248b-384e-4b57-b825-8a2354094bb2
category: getting-started
tags: hello-world|nothing-special
title: Hello World
url: https://github.com/soasme/zetanote/blob/master/README.md
date: 2018-03-01
author: Ju Lin <soasme@gmail.com>
description: This is definitely an awesome start! 

Hey, this is a hello world.
If you are in vim editor, type ESC :x to save and exit.
```

## Commands

```
# Show all notes
$ zeta ls

# Show key+tags
$ zeta ls -f tags

# Show key+title
$ zeta ls --field title

# Open in $EDITOR
$ zeta open 2244248b-384e-4b57-b825-8a2354094bb2

# Show note
$ zeta cat 2244248b-384e-4b57-b825-8a2354094bb2

# Count words
$ zeta ls -f text | wc -c

# Count notes
$ zeta ls | wc -l

# Filter by month
$ zeta ls -f date | grep '2018-03'
```
