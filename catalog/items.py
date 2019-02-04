from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import NailPolishBrands, Base, BrandItems, Users

engine = create_engine('sqlite:///nailpolishesstore.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = Users(uname="KOMALI", email="komalikotipalli@gmail.com")
session.add(user1)
session.commit()

# BRAND ONE
brand1 = NailPolishBrands(name="KIARA SKY", u_id=1)
session.add(brand1)
session.commit()

brandItem1 = BrandItems(name="Ice For you", description="Gel Polish",
                        price="$12.99", nail_polish_brands=brand1, u_id=1)
session.add(brandItem1)
session.commit()

brandItem2 = BrandItems(name="Love at frost bite", description="Gel Polish",
                        price="$12.99", nail_polish_brands=brand1, u_id=1)
session.add(brandItem2)
session.commit()

brandItem3 = BrandItems(name="Naughty List", description="Dip Powder",
                        price="$14.99", nail_polish_brands=brand1, u_id=1)
session.add(brandItem3)
session.commit()

brandItem4 = BrandItems(name="Mauve a Lil", description="Dip Powder",
                        price="$14.99", nail_polish_brands=brand1, u_id=1)
session.add(brandItem4)
session.commit()

brandItem5 = BrandItems(name="fancynator", description="Nail Lacquer",
                        price="$8.50", nail_polish_brands=brand1, u_id=1)
session.add(brandItem5)
session.commit()

# BRAND TWO
brand2 = NailPolishBrands(name="CHINA GLAZE", u_id=1)
session.add(brand2)
session.commit()

brandItem1 = BrandItems(name="Peachy Keen", description="Gel Polish",
                        price="$12.99", nail_polish_brands=brand2, u_id=1)
session.add(brandItem1)
session.commit()

brandItem2 = BrandItems(name="Night and Slay",
                        description="Holographic Glitter Polish",
                        price="$12.99", nail_polish_brands=brand2, u_id=1)
session.add(brandItem2)
session.commit()

brandItem3 = BrandItems(name="Frost Bite", description="Gel Polish",
                        price="$14.99", nail_polish_brands=brand2, u_id=1)
session.add(brandItem3)
session.commit()

brandItem4 = BrandItems(name="Lets Shell Ebrate",
                        description="Shimmery Polish", price="$14.99",
                        nail_polish_brands=brand2, u_id=1)
session.add(brandItem4)
session.commit()

brandItem5 = BrandItems(name="Pretty Fit", description="Gel Polish",
                        price="$8.50", nail_polish_brands=brand2, u_id=1)
session.add(brandItem5)
session.commit()

# BRAND THREE
brand3 = NailPolishBrands(name="REVLON", u_id=1)
session.add(brand3)
session.commit()

brandItem1 = BrandItems(name="Holochrome", description="Nail Enamel",
                        price="$5.47", nail_polish_brands=brand3, u_id=1)
session.add(brandItem1)
session.commit()

brandItem2 = BrandItems(name="Chameleon", description="Nail Enamel",
                        price="$8.18", nail_polish_brands=brand3, u_id=1)
session.add(brandItem2)
session.commit()

brandItem3 = BrandItems(name="Colour Stay", description="Gel envy",
                        price="$4.97", nail_polish_brands=brand3, u_id=1)
session.add(brandItem3)
session.commit()

brandItem4 = BrandItems(name="Magnetic", description="Gel Enamel",
                        price="$3.97", nail_polish_brands=brand3, u_id=1)
session.add(brandItem4)
session.commit()

brandItem5 = BrandItems(name="Extravagant", description="Nail Enamel",
                        price="$5.66", nail_polish_brands=brand3, u_id=1)
session.add(brandItem5)
session.commit()

print ("added menu items!")
