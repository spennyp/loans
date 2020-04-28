from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Date
import yaml
import bcrypt
from datetime import datetime

# Setting up database connection
secrets = yaml.load(open("secrets.yaml"), Loader=yaml.FullLoader) # Must add secrets.yaml to run the application
engine = create_engine(f'mysql+pymysql://{secrets["dbUsername"]}:{secrets["dbPassword"]}@{secrets["dbHost"]}:3306/{secrets["dbName"]}', convert_unicode=True)
Base = declarative_base()
dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = dbSession.query_property() # Allow querying on models


class UserModel(Base):
    __tablename__ = "user"
    id = Column("id", Integer, primary_key=True)
    email = Column("email", String)
    password = Column("password", String)
    authenticated = Column("authenticated", Boolean)
    creationDate = Column("creationDate", DateTime)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.authenticated = True
        self.creationDate = datetime.today()

    @staticmethod
    def getUserForEmail(email): # Returns the user if it exists, otherwise None
        return UserModel.query.filter(UserModel.email == email).first()

    def login(self, pw):
        hashedPw = self.password.encode("utf-8")
        validated = bcrypt.checkpw(pw, hashedPw)
        if validated:
            self.authenticated = True
            dbSession.commit()
        return validated

    def logout(self):
        self.authenticated = False
        dbSession.commit()   

    def verify(self, jwtId):
        return True if self.id == jwtId and self.authenticated == True else False     


class UserInfoModel(Base):
    __tablename__ = "userInfo"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    
    def __init__(self, id, name):
        self.id = id
        self.name = name


class LoanModel(Base):
    __tablename__ = "loan"
    id = Column("id", Integer, primary_key=True)
    creatorId = Column("creatorId", Integer)
    loanerId = Column("loanerId", Integer)
    loaneeId = Column("loaneeId", Integer)
    amount = Column("amount", Float)
    interstRate = Column("interestRate", Float)
    termMonths = Column("termMonths", Integer)
    startDate = Column("startDate", Date)
    accepted = Column("accepted", Boolean)
    active = Column("active", Boolean)
    creationDate = Column("creationDate", DateTime)

    def __init__(self, creatorId, loanerId, loaneeId, amount, interestRate, termMonths, startDate):
        self.creatorId = creatorId
        self.loanerId = loanerId
        self.loaneeId = loaneeId
        self.amount = amount
        self.interstRate = interestRate
        self.termMonths = termMonths
        self.startDate = startDate
        self.creationDate = datetime.today()
        self.accepted = False
        self.active = False

