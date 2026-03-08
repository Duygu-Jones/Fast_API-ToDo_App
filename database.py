from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# ==========PSOTGRESQL ===============
# PostgreSQL veritabanı için PgAdmin4 te oludturdugumuz DB bağlantı URL'si; 
# (postgresql://kullanici_adi:sifre@host:port/veritabani_adi)
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:test1234!@localhost/TodoAppDatabase'

# PostgreSQL icin Veritabanı motorunu 
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# ==========SQLITE ===============
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine =create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine)

Base = declarative_base()
