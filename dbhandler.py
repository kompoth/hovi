from sqlalchemy import create_engine, inspect, or_, and_
from sqlalchemy.orm import Session

from tables import Tile


class LikeTileError(Exception):
    pass


class DBHandler:

    def __init__(self, url):
        self.__engine = create_engine(url,
        # meh this mutes warnings but I don't understand it ...
                        connect_args={"check_same_thread": False})
        if not inspect(self.__engine).has_table("periods"):
            Tile.metadata.create_all(self.__engine)

    def get_num_of_type(self, tile_type):
        tiles = None
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(Tile.ttype == tile_type)
        return tiles.count()

    def get_tile(self, side, tile_type=None):
        mask = or_(Tile.first_side == side, Tile.second_side == side)
        if tile_type is not None:
            mask = and_(mask, Tile.ttype == tile_type)
        with Session(self.__engine) as session:
            tiles = session.query(Tile).filter(mask)
        return list(tiles)

    def add_tile(self, first_side, second_side, tile_type):
        sides = [first_side, second_side]
        sides.sort()
        for side in sides:
            like_tiles = self.get_tile(side, tile_type)
            if len(like_tiles):
                str_list = "".join([f"{x}\n" for x in like_tiles])
                raise LikeTileError(f"Like tiles in database:\n{str_list}")

        index = self.get_num_of_type(tile_type) + 1
        tile = Tile(public_id=index, ttype=tile_type,
                    first_side=sides[0], second_side=sides[1])
        with Session(self.__engine) as session:
            session.add(tile)
            session.commit()
