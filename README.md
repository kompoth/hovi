# Hvts ov Insanity - Thy path to madness #
Hovi is a telegram bot designed to make it easier to find map tiles while
playing *one horror tabletop game*. Add all your tiles to bot's database and
mark them physically, using some small pieces of paper with indices.

Indexing system is quite simple: each tile is enumerated in the order it was
added to a database. 

Hovi is also my self-education project.

## Requirements ##
- Python 3.6+
- pyTelegramBotAPI 4.4.0+
- SQLAlchemy

## Configuration ##
Put `config.ini` near `bot.py` script with following values:
```
[telegram]
token = <telegram API token>
editors = <list of ids of users allowed to change data>

[database]
ftypes = corridor,square,hall
sources = base
```
*ftypes* are types of tiles that you have. You can use any classification
you like, for example form factors.
*sources* are names of game sets and extensions you are using.
Both *ftypes* and *sources* lists are very important, especially if there are
tiles with equal names from different sets.

## Usage ##
Currently it is very simple: just configure bot and run it with
```
python bot.py
```
You will see live log then.

## TODO ##
- Create a separate directory for python modules 
- Add some new commands:
  - add to/delete from editors list
  - edit and delete tiles
- Save tile scans to database (do we need this?)
- WTF are those SQLite3 ProgrammingError messages???
