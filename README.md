# Hvts ov Insanity - Thy path to madness #
HovI is a telegram bot designed to make it easier to find map tiles while
playing *one horror tabletop game*. It should be used with a simple indexing 
system: just attach small papers to tiles, like in some kind of a file cabinet,
then add each tile to HovI database, marking it with a corresponding number.
When game app tells you to get a new tile, just send its name to HovI and it
will answer you with this tile's index.

HovI is also my self-education project.

## Requirements ##
- Python 3.6+
- pyTelegramBotAPI 4.4.0+
- SQLAlchemy

## Configuration ##
There is `example-config.ini` file, where Telegram API token must be specified
as well as a list of telegram ids of users that are allowed to changa database.

## TODO ##
- Move bot stuff to separate module
- Create separate directory for python modules 
- Add new commands:
  - add to/delete from editors list
  - edit and delete tiles
- Save tile scans to database
- WTF are those SQLite3 ProgrammingError messages???
