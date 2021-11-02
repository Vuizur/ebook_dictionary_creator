# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Word(Base):
    __tablename__ = 'word'

    word_id = Column(Integer, primary_key=True)
    pos = Column(String)
    canonical_form = Column(String)
    romanized_form = Column(String)
    genitive_form = Column(String)
    adjective_form = Column(String)
    nominative_plural_form = Column(String)
    genitive_plural_form = Column(String)
    ipa_pronunciation = Column(String)
    lang = Column(String)
    word = Column(String)
    lang_code = Column(String)

    words = relationship(
        'Word',
        secondary='form_of_word',
        primaryjoin='Word.word_id == form_of_word.c.base_word_id',
        secondaryjoin='Word.word_id == form_of_word.c.word_id'
    )


t_form_of_word = Table(
    'form_of_word', metadata,
    Column('word_id', ForeignKey('word.word_id'), nullable=False),
    Column('base_word_id', ForeignKey('word.word_id'), nullable=False)
)


class Sense(Base):
    __tablename__ = 'sense'

    sense_id = Column(Integer, primary_key=True)
    word_id = Column(ForeignKey('word.word_id'), nullable=False)

    word = relationship('Word')


class Glos(Base):
    __tablename__ = 'gloss'

    gloss_id = Column(Integer, primary_key=True)
    sense_id = Column(ForeignKey('sense.sense_id'))
    gloss_string = Column(String)

    sense = relationship('Sense')