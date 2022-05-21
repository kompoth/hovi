from sqlalchemy import create_engine, inspect, func, and_
from sqlalchemy.orm import Session

from tables import Tile


class DBHandler:
    def __init__(self, url):
        self.__engine = create_engine(url,
        # meh this mutes warnings but I don't understand it ...
                        connect_args={"check_same_thread": False})
        if not inspect(self.__engine).has_table("periods"):
            Tile.metadata.create_all(self.__engine)

    def get_max_index_for_type(self, ftype):
        """Get greatest index for tiles of given form type"""
        res = None
        with Session(self.__engine) as session:
            max_ids_query = session.query(func.max(Tile.public_id))
            res = max_ids_query.filter(Tile.ftype == ftype).scalar()
        return res

    def get_tile(self, name, ftype=None, source=None):
        """Return list of tiles with given properties"""
        mask = Tile.name == name
        mask = mask if ftype is None else and_(mask, Tile.ftype == ftype)
        mask = mask if source is None else and_(mask, Tile.source == source)
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(mask)
        return list(tiles)

    def add_tile(self, name, ftype, source):
        """Add tile to database"""
        max_index = self.get_max_index_for_type(ftype)
        index = 1 if max_index is None else max_index + 1
        tile = Tile(public_id=index, name=name, ftype=ftype,
                    source=source)
        with Session(self.__engine) as session:
            session.add(tile)
            session.commit()
