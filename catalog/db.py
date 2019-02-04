import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)


class NailPolishBrands(Base):
    __tablename__ = 'nail_polish_brands'
    """docstring for NailPolishBrands"""
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    u_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name
        }


class BrandItems(Base):
    __tablename__ = 'brand_items'
    name = Column(String(80), nullable=False)
    description = Column(String(100))
    id = Column(Integer, primary_key=True)
    price = Column(String(5))
    item_id = Column(Integer, ForeignKey('nail_polish_brands.id'))
    nail_polish_brands = relationship(NailPolishBrands)
    u_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price
        }


engine = create_engine('sqlite:///nailpolishesstore.db')
Base.metadata.create_all(engine)
