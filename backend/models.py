from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Date
import yaml
import bcrypt
from datetime import datetime
import numpy as np


# Setting up database connection
secrets = yaml.load(open("secrets.yaml"), Loader=yaml.FullLoader) # Must add secrets.yaml to run the application
engine = create_engine(f'mysql+pymysql://{secrets["dbUsername"]}:{secrets["dbPassword"]}@{secrets["dbHost"]}:3306/{secrets["dbName"]}', convert_unicode=True)
Base = declarative_base()
dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = dbSession.query_property() # Allow querying on models


class UserModel(Base):
    __tablename__ = "user"
    id = Column("id", Integer, primary_key=True)
    firstName = Column("firstName", String)
    lastName = Column("lastName", String)
    email = Column("email", String)
    password = Column("password", String)
    authenticated = Column("authenticated", Boolean)
    creationDate = Column("creationDate", DateTime)

    def __init__(self, firstName, lastName, email, password):
        self.firstName = firstName
        self.lastName = lastName
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

    def getLoans(self):
        return LoanModel.query.filter(LoanModel.loaneeId == self.id or LoanModel.loanerId == self.id)


class PaymentModel(Base):
    __tablename__ = "payment"
    id = Column("id", Integer, primary_key=True)
    userId = Column("userId", Integer)
    bank = Column("bank", Integer)
    creationDate = Column("creationDate", DateTime)

    def __init__(self, userId, bank):
        self.userId = userId
        self.bank = bank
        self.creationDate = datetime.today()


class TransactionModel(Base):
    __tablename__ = "transaction"
    id = Column("id", Integer, primary_key=True)
    loanId = Column("loanId", Integer)
    amount = Column("amount", Integer)
    fromPaymentId = Column("fromPaymentId", Integer)
    toPaymentId = Column("toPaymentId", Integer)
    complete = Column("complete", Boolean)
    creationDate = Column("creationDate", DateTime)
    completionDate = Column("completionDate", DateTime)

    def __init__(self, loanId, amount, fromPaymentId, toPaymentId):
        self.loanId = loanId
        self.amount = amount
        self.fromPaymentId = fromPaymentId
        self.toPaymentId = toPaymentId
        self.complete = False
        self.creationDate = datetime.today()

        # TODO: TEMP: just used while EFT is not set up, completion should be triggered by the EFT payment API
        self.complete = True
        self.completionDate = datetime.today()


class LoanModel(Base):
    __tablename__ = "loan"
    id = Column("id", Integer, primary_key=True)
    loanName = Column("loanName", String)
    creatorId = Column("creatorId", Integer)
    loanerId = Column("loanerId", Integer)
    loaneeId = Column("loaneeId", Integer)
    amount = Column("amount", Float)
    interestRate = Column("interestRate", Float)
    termMonths = Column("termMonths", Integer)
    monthlyPayment = Column("monthlyPayment", Float)
    startDate = Column("startDate", Date)
    accepted = Column("accepted", Boolean)
    declined = Column("declined", Boolean)
    active = Column("active", Boolean)
    creationDate = Column("creationDate", DateTime)

    def __init__(self, loanName, creatorId, loanerId, loaneeId, amount, interestRate, termMonths, startDate):
        self.loanName = loanName
        self.creatorId = creatorId
        self.loanerId = loanerId
        self.loaneeId = loaneeId
        self.amount = amount
        self.interestRate = interestRate / 100 # This is the nominal annual interest rate 
        self.termMonths = termMonths
        self.startDate = startDate
        self.creationDate = datetime.today()
        self.accepted = False
        self.declined = False
        self.active = False
        self.monthlyPayment = -float(np.pmt(self.interstRate/12, termMonths, amount))

    @staticmethod
    def getLoanForId(id):
        return LoanModel.query.filter(LoanModel.id == id).first()

    def accept(self, doesAccept):
        if not self.declined and not self.accepted: # If it has already been declined, it cannot later be accepted
            self.accepted = doesAccept
            self.declined = not doesAccept
            self.active = doesAccept
            dbSession.commit() 
            return True
        else:
            return False

    def __computeTransactionSums(self): # Gets all the transactions and buckets them into the period in which they were paid
        completedTransactions = TransactionModel.query.filter(TransactionModel.loanId == self.id and TransactionModel.complete == True)
        currentBucket = max((datetime.today().year - self.startDate.year) * 12 + (datetime.today().month - self.startDate.month), 0)

        # Find the last payment bucket, it may be outside of the termMonths
        largestBucket = 0
        for t in completedTransactions:
            date = t.completionDate
            bucket = (date.year - self.startDate.year) * 12 + (date.month - self.startDate.month)
            if bucket > largestBucket:
                largestBucket = bucket

        largestBucket = max(largestBucket, self.termMonths + 1)
        transactionSums = [0] * largestBucket

        # Bucket the transactions
        for t in completedTransactions:
            date = t.completionDate
            bucket = (date.year - self.startDate.year) * 12 + (date.month - self.startDate.month)
            transactionSums[bucket] += t.amount

        # Add in future payments assuming monthly payment will be made
        if currentBucket < largestBucket:
            transactionSums[currentBucket] = max(transactionSums[currentBucket], self.monthlyPayment)
            for i in range(currentBucket + 1, self.termMonths + 1):
                transactionSums[i] = self.monthlyPayment

        return (transactionSums, currentBucket)

    def computeDetails(self):
        monthlyInterestRate = self.interestRate / 12
        transactionSums, currentBucket = self.__computeTransactionSums()
        interest = [0]
        principal = [0]
        balance = [self.amount]
        overdue = [0]

        for i in range(1, len(transactionSums)):
            # The order these are computed is important!
            interest.append(balance[i-1]*monthlyInterestRate)
            principal.append(transactionSums[i] - interest[i])
            balance.append(balance[i-1] + interest[i] - transactionSums[i])
            overdue.append(min(0, overdue[i-1]*(1+monthlyInterestRate) + transactionSums[i] - self.monthlyPayment))

        dueThisMonth = min(0, self.monthlyPayment - transactionSums[currentBucket])
        ammountRemaining = balance[currentBucket]
        totalInterestPaidAtEnd = sum(interest)

        return {"currentBucket": currentBucket, "dueThisMonth": dueThisMonth, "ammountRemaining": ammountRemaining, "payments": transactionSums, "totalInterestPaidAtEnd": totalInterestPaidAtEnd, "balance": balance, "overdue": overdue, "interest": interest, "principal": principal}




