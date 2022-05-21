from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Tile(Base):
    __tablename__ = "tiles"

    primary_id = Column(Integer, primary_key=True)
    public_id = Column(Integer, nullable=False)
    name = Column(String)
    ftype = Column(String)
    source = Column(String)

    def __repr__(self):
        return f"<{self.ftype}:{self.public_id}:{self.name}>"

    def __str__(self):
        return f"{self.public_id}. {self.name} ({self.ftype}), {self.source}"
