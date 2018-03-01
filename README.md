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
# zeta open ##### Will prompt default $EDITOR
# zeta ls
```

The note content includes meta and note text.
Note meta are formed line by line in format like `key: value`.
`key` is essential.
An empty line needs to be placed between meta and note text.
Below is an example note:

```
key: 2244248b-384e-4b57-b825-8a2354094bb2
category: getting-started
tags: hello-world|nothing-special
title: Hello World
url: https://github.com/soasme/zetanote/blob/master/README.md

Hey, this is a hello world.
If you are in vim editor, type ESC :x to save and exit.
```

## Commands

```
$ zeta ls
$ zeta ls -f tags
$ zeta ls --field title
$ zeta open 2244248b-384e-4b57-b825-8a2354094bb2
$ zeta cat 2244248b-384e-4b57-b825-8a2354094bb2
```
