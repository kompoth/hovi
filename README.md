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
Put `config.ini` near `bot.py` script with bot configuration variables. Use
`example-config.ini` as a reference. 

## Usage ##
Currently it is very simple: just configure bot and run it with
```
python bot.py
```
You will see live log then.

## TODO ##
- Move config to utils module to make it easily accessable from any module
- Move bot stuff to a separate module
- Create a separate directory for python modules 
- Add some new commands:
  - add to/delete from editors list
  - edit and delete tiles
- Save tile scans to database (do we need this?)
- WTF are those SQLite3 ProgrammingError messages???
