from sqlalchemy import create_engine, inspect, func, and_
from sqlalchemy.orm import Session
from itertools import groupby
from operator import attrgetter
import logging

from tables import Tile
from utils import DBPATH


class DBHandler:
    __uri = f"sqlite:///{DBPATH}"

    def __init__(self):
        self.__engine = create_engine(self.__uri,
        # meh this mutes warnings but I don't understand it ...
                        connect_args={"check_same_thread": False})
        if not inspect(self.__engine).has_table("periods"):
            Tile.metadata.create_all(self.__engine)

    @property
    def uri(self):
        return self.__uri

    def __max_ftype_index(self, ftype):
        """Get the greatest index for tiles of given ftype"""
        max_id = None
        mask = Tile.ftype == ftype
        with Session(self.__engine) as session:
            max_id = session.query(func.max(Tile.public_id)).filter(mask)
        return max_id.scalar()

    def find_tiles(self, name, ftype=None, source=None):
        """Return a fancy list of tiles with given properties"""
        mask = Tile.name.contains(name.lower())
        mask = mask if ftype is None else and_(mask, Tile.ftype == ftype)
        mask = mask if source is None else and_(mask, Tile.source == source)
        tiles = None
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(mask).order_by(Tile.public_id)

        fancy_list = []
        for tile in tiles:
            fancy = f"*{tile.ftype}-{tile.public_id}.* " + \
                    f"{tile.name.capitalize()} ({tile.source})"
            fancy_list.append(fancy)
        return "\n".join(fancy_list)

    def list_pieces(self, ftype):
        """Get a fancy list of pieces"""
        tiles = []
        mask = Tile.ftype == ftype
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(mask).order_by(Tile.public_id)
        keyfunc = attrgetter("public_id") # function to extract Tile's id
        pieces = [list(g) for k, g in groupby(tiles, keyfunc)]

        fancy_list = []
        for tiles in pieces:
            fancy = f"*{tiles[0].ftype}-{tiles[0].public_id}.* " + \
                    ", ".join([x.name.capitalize() for x in tiles]) + \
                    f" ({tiles[0].source})"
            fancy_list.append(fancy)
        return "\n".join(fancy_list)

    def add_tiles(self, names, ftype, source):
        """Add list of tiles to database"""
        if isinstance(names, str):
            names = [names]
        max_index = self.__max_ftype_index(ftype)
        index = 1 if max_index is None else max_index + 1
        with Session(self.__engine) as session:
            for name in names:
                tile = Tile(public_id=index, name=name.lower(),
                            ftype=ftype, source=source)
                session.add(tile)
            session.commit()
