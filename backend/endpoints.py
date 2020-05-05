from flask import request, jsonify
from flask_restful import Resource, Api
from models import *
import json
import bcrypt
import traceback
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from datetime import datetime
from pprint import pprint
from errors import *
from sqlalchemy import or_, and_


class Test(Resource):
    @jwt_required
    def put(self):
        return "SUCCESS", 200

class User(Resource):
    @jwt_required
    def get(self): # Get the users information
        try:
            payload = request.get_json()
            # TODO
            return "TODO"
        except Exception as e:
            return f"Error: {e}", 400

    @jwt_required
    def put(self): # Update the users information
        # TODO
        return "Put"

    def post(self): # Create a new user
        try:
            payload = request.get_json()
            firstName = payload["firstName"]
            lastName = payload["lastName"]
            email = payload["email"]
            password = payload["password"].encode("utf-8")

            # Check if and account already exists for that email
            existingUser = UserModel.getUserForEmail(email)
            if existingUser is not None:
                return "Error: Account already exists for this email", 409 

            salt = bcrypt.gensalt() # Don't need to store the salt since bcrypt puts it at the beginning of the password
            hashedPw = bcrypt.hashpw(password, salt)
            newUser = UserModel(firstName, lastName, email, hashedPw)
            dbSession.add(newUser)
            dbSession.flush() # To fetch the id
            id = newUser.id # This id is used in the jwt
            dbSession.commit()

            resp = jsonify({"login": True})
            return resp, 200
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}", 400


class Loan(Resource):
    @jwt_required
    def get(self): # Get all loans and their detailed information
        try:
            jwtId = get_jwt_identity()
            user = UserModel.getUserForId(jwtId)                
            loans = user.getLoans()
            loanDetails = []
            totalLoanedAmount = 0
            totalProjectedInterestPaid = 0
            totalCurrentInterestPaid = 0
            for loan in loans:
                details = loan.computeDetails()
                details["loanName"] = loan.loanName
                details["loaner"] = loan.loanerId == user.id
                details["interestRate"] = loan.interestRate
                details["startDate"] = loan.startDate.strftime("%d-%b-%Y")
                details["termMonths"] = loan.termMonths
                otherUserId =  loan.loaneeId if (loan.loanerId == user.id) else loan.loanerId
                otherUserName = UserModel.getUserForId(otherUserId).firstName
                details["withPerson"] = otherUserName
                loanDetails.append(details)
                totalLoanedAmount += details["loanValue"]
                totalProjectedInterestPaid += details["totalInterestPaidAtEnd"]
                totalCurrentInterestPaid += details["currentInterestPaid"]

            overallSummary = {
                "totalLoanedAmount": totalLoanedAmount,
                "totalProjectedInterestPaid": totalProjectedInterestPaid,
                "totalCurrentInterestPaid": totalCurrentInterestPaid
            }

            return {"success": True, "overallSummary": overallSummary, "loanDetails": loanDetails, "msg": "returned loan details"}, 200
        except Exception as e:
            traceback.print_exc()
            raise(InternalServerError(e))

    @jwt_required
    def put(self): # Update the loan info
        # TODO
        return "Put"

    @jwt_required
    def post(self): # Create a new loan
        try:
            payload = request.get_json()
            print(payload)
            try:
                loanName = payload["loanName"]
                loaner = payload["loaner"]
                otherUserEmail = payload["otherUserEmail"]
                amount = payload["amount"]
                interestRate = payload["interestRate"]
                termMonths = payload["termMonths"]
                startDate = payload["startDate"] # Format: 2020-04-28
            except:
                return f"Error: Invalid payload - {payload}", 400

            jwtId = get_jwt_identity()

            # Make sure the other user is not themselves
            user = UserModel.getUserForId(jwtId)
            if otherUserEmail == user.email:
                return {"success": False, "msg":"Self loan"}, 400

            # Make sure the other users exist
            otherUser = UserModel.getUserForEmail(otherUserEmail)
            if otherUser is None:
                return {"success": False, "msg":"Invalid email"}, 400 

            # Make sure they dont already have a loan with this name
            if LoanModel.query.filter(and_(or_(LoanModel.loanerId == user.id, LoanModel.loaneeId == user.id), LoanModel.loanName == loanName)).first() is not None:
                return {"success": False, "msg": "Name taken"}, 400

            loanerUserId = user.id if loaner else otherUser.id
            loaneeUserId = otherUser.id if loaner else user.id

            creatorId = jwtId
            newLoan = LoanModel(loanName, creatorId, loanerUserId, loaneeUserId, amount, interestRate, termMonths, startDate)
            dbSession.add(newLoan)
            dbSession.commit()
            return {"success": True}, 200
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}", 400

    @jwt_required
    def delete(self): # Terminate the loan
        # TODO
        pass


class AcceptLoan(Resource): 
    @jwt_required
    def post(self): # Accept or decline the loan
        try:
            payload = request.get_json()
            email = payload["email"]
            loanId = payload["loanId"]
            doesAccept = payload["doesAccept"]
            
            user = UserModel.getUserForEmail(email)
            loan = LoanModel.getLoanForId(loanId)
            if user is None or loan is None:
                return "Error: Not found", 401

            # Make sure it is the correct user, and this is the user that should be accepting the loan
            jwtId = get_jwt_identity()
            if not user.verify(jwtId):
                return "Error: Unauthortized", 401

            # Make sure this user is the one who should be accepting
            if loan.creatorId != user.id and (loan.loanerId == user.id or loan.loaneeId == user.id):
                result = loan.accept(doesAccept)
                if result == True:
                    return "Success", 200
                else: 
                    return "Error: Loan already accepted or declined", 400
            else:
                return "Error: Unauthortized", 401
        except Exception as e:
            return f"Error: {e}", 400


class Transaction(Resource): 
    @jwt_required
    def get(self): # Get all transactions made by user
        try:
            pass

        except Exception as e:
            return f"Error: {e}", 400

    def post(self): # Create a transaction on a loan
        try:
            payload = request.get_json()
            # TODO:
            return "success", 200
        except Exception as e:
            return f"Error: {e}", 400

