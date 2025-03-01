from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Подключение к базе данных
DATABASE_URL = "sqlite:///DS_TG_DB.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Таблица users
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(String, nullable=False, unique=True)
    greetings = Column(String)
    linked_users_id = Column(Integer, ForeignKey('linked_users.id', ondelete="CASCADE"), nullable=True)
    
    linked_users = relationship("LinkedUser", back_populates="users")

# Таблица linked_users
class LinkedUser(Base):
    __tablename__ = 'linked_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_name = Column(String, nullable=False, unique=True)
    logs = Column(String)
    
    users = relationship("User", back_populates="linked_users", cascade="all, delete")
    faceit_users = relationship("FaceitUser", back_populates="linked_user", cascade="all, delete")

# Таблица faceit_users
class FaceitUser(Base):
    __tablename__ = 'faceit_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    linked_users_id = Column(Integer, ForeignKey('linked_users.id', ondelete="CASCADE"), nullable=False)
    faceit_name = Column(String, nullable=False, unique=True)
    faceit_lvl = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    
    linked_user = relationship("LinkedUser", back_populates="faceit_users")

# Создаем таблицы
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

# Функция для проверки существования записей в базе данных
def check_bot_existence():
    tables = {
        "User": session.query(User).count(),
        "LinkedUser": session.query(LinkedUser).count(),
        "FaceitUser": session.query(FaceitUser).count()
    }
    
    if any(tables.values()):
        print("Бот успешно проверен и готов к запуску!")
        for table, count in tables.items():
            print(f"{table}: {count} записей")
    else:
        print("Нет записей в базе данных.")

# Проверка
check_bot_existence()

