from datetime import date
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, relation, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Date
import os

Base = declarative_base()
uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.join(__file__, '..')), 'data.db')
engine = create_engine(uri)
Session = sessionmaker(bind=engine)
session = Session()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, unique=True)
    url = Column(String)
    passcode = Column(String)
    episode_id = Column(Integer, ForeignKey('episodes.id'))
    episode = relationship('Episode', back_populates='links')

    def __repr__(self) -> str:
        return "<Link name={} episode={} >".format(self.name, str(self.episode))
    
    def __str__(self) -> str:
        return "{} {} {}".format(str(self.episode.show), str(self.episode), self.name)

class Episode(Base):
    __tablename__ = 'episodes'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, unique=True)
    show_id = Column(Integer, ForeignKey('shows.id'))
    show = relationship('Show', back_populates='episodes')
    links = relationship('Link', back_populates='episode')

    def __repr__(self) -> str:
        return "<Episode id={} name={} show={} link_count={} >".format(self.id, self.name, self.show, len(self.links))
    
    def __str__(self) -> str:
        return "{} {}".format(self.show.name, self.name)


class Show(Base):
    __tablename__ = 'shows'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False, unique=True)
    original_name = Column(String)
    img = Column(String)
    season = Column(Integer)
    episode_number = Column(Integer)
    last_update = Column(Date)
    meijumi_id = Column(String, unique=True)

    episodes = relationship('Episode', back_populates='show')

    def __repr__(self) -> str:
        return "<Show id={} name={} url={} last_update={} >".format(self.id, self.name, self.meijumi_id, self.last_update)
    
    def __str__(self) -> str:
        return self.name

# Base.metadata.create_all(engine)
# session.commit()


