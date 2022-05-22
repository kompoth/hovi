from sqlalchemy import create_engine, inspect, func, and_
from sqlalchemy.orm import Session

from tables import Tile


class DBHandler:
    def __init__(self, uri):
        self.__engine = create_engine(uri,
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

    def search(self, name, ftype=None, source=None):
        """Return fancy list of tiles with given properties"""
        mask = Tile.name.contains(name.lower())
        mask = mask if ftype is None else and_(mask, Tile.ftype == ftype)
        mask = mask if source is None else and_(mask, Tile.source == source)
        tiles = []
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(mask)
        fancy_list = []
        for tile in tiles:
            fancy = f"*{tile.public_id}.* {tile.name.capitalize()} " + \
                    f"({tile.ftype}, {tile.source})"
            fancy_list.append(fancy)
        return fancy_list

    def add_tiles(self, names, ftype, source):
        """Add list of tiles to database"""
        if isinstance(names, str):
            names = [names]
        max_index = self.get_max_index_for_type(ftype)
        index = 1 if max_index is None else max_index + 1
        with Session(self.__engine) as session:
            for name in names:
                tile = Tile(public_id=index, name=name.lower(),
                            ftype=ftype, source=source)
                session.add(tile)
            session.commit()
