from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Tile(Base):
    __tablename__ = "tiles"

    primary_id = Column(Integer, primary_key=True)
    public_id = Column(Integer, nullable=False)
    ttype = Column(String)
    first_side = Column(String)
    second_side = Column(String)

    def __repr__(self):
        return f"[{self.ttype}:{self.public_id}]"

    def __str__(self):
        return f"{self.__repr__()} {self.first_side}, {self.second_side}"
