# Zetanote

Note service with unlimited meta information added for better organizing.

Zetanote loads a flat file database into memory for high performance searching and organizing.

## Requirements

Zetanote supports Python 3.6+.

## Installation

```
$ pip install zetanote
```

## Usage

```
# Start instaweb
$ zeta instaweb start

# Open in browser
$ zeta instaweb open

# Stop instaweb
$ zeta instaweb stop

# Restart instaweb
$ zeta instaweb restart
```

## Development

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

## Support

* No support via twitter / email.
* Please report Zetanote OSS issues on [GitHub Issue](https://github.com/soasme/zetanote/issues)

## License

Please see LICENSE for licensing details.

## Author

Ju Lin, [@soasme](https://twitter.com/soasme).
