from flask import request, jsonify
from flask_restful import Resource, Api
from models import (dbSession, UserModel, LoanModel)
import json
import bcrypt
import traceback
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from datetime import datetime
from pprint import pprint


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

            accessToken = create_access_token(identity = id)
            refreshToken = create_refresh_token(identity = id)
            return {"status": "success", "accessToken": accessToken, "refreshToken": refreshToken}, 200
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}", 400


# TODO: Implement oAuth later on
class Login(Resource):
    def post(self):
        try:
            payload = request.get_json()
            email = payload["email"]
            pw = payload["password"].encode("utf-8")
            
            user = UserModel.getUserForEmail(email)
            if user is None:
                return "Error: Auth failed", 401 # Don't want to say no email for that account for security reasons

            validated = user.login(pw)

            if validated:
                accessToken = create_access_token(identity = user.id)
                refreshToken = create_refresh_token(identity = user.id)
                return {"status": "success", "accessToken": accessToken, "refreshToken": refreshToken}, 200
            else:
                return "Incorrect password", 401
        except Exception as e:
            return f"Error: {e}", 400


class Logout(Resource):
    @jwt_required
    def post(self):
        try:
            payload = request.get_json()
            email = payload["email"]
            
            user = UserModel.getUserForEmail(email)
            if user is None:
                return "Error: No account with that email", 401

            # Make sure it is the correct user
            jwtId = get_jwt_identity()
            if not user.verify(jwtId):
                return "Error: Unauthortized", 401

            user.logout()
            return "Success", 200
        except Exception as e:
            return f"Error: {e}", 400


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        try:
            payload = request.get_json()
            email = payload["email"]
            user = UserModel.getUserForEmail(email)

            # Make sure it is the correct user
            jwtId = get_jwt_identity()
            if user is None or not user.verify(jwtId):
                return "Error: Unauthortized", 401

            accessToken = create_access_token(identity = jwtId)
            return {'access_token': accessToken}, 200
        except Exception as e:
            return f"Error: {e}", 400


class Loan(Resource):
    @jwt_required
    def get(self): # Get all loans and their detailed information
        try:
            payload = request.get_json()
            email = payload["email"]

            user = UserModel.getUserForEmail(email)

            if user is None:
                return "Error: Not found", 400

            jwtId = get_jwt_identity()
            if not user.verify(jwtId):
                return "Error: Unauthortized", 400

            loans = user.getLoans()
            loanDetails = []
            for loan in loans:
                details = loan.computeDetails()
                details["loanName"] = loan.loanName
                details["loaner"] = loan.loanerId == user.id
                details["interestRate"] = loan.interestRate
                details["startDate"] = loan.startDate.strftime("%d-%b-%Y")
                details["termMonths"] = loan.termMonths
                loanDetails.append(details)

            return {"status": "success", "loanDetails": loanDetails}, 200
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}", 400

    @jwt_required
    def put(self): # Update the loan info
        # TODO
        return "Put"

    @jwt_required
    def post(self): # Create a new loan
        try:
            payload = request.get_json()
            try:
                loanName = payload["loanName"]
                loanerEmail = payload["loanerEmail"]
                loaneeEmail = payload["loaneeEmail"]
                amount = payload["amount"]
                interestRate = payload["interestRate"]
                termMonths = payload["termMonths"]
                startDate = payload["startDate"] # Format: 2020-04-28
            except:
                return f"Error: Invalid payload - {payload}", 400

            # Make sure the users exist
            loanerUser = UserModel.getUserForEmail(loanerEmail)
            loaneeUser = UserModel.getUserForEmail(loaneeEmail)
            if loanerUser is None or loaneeUser is None:
                return "Error: Invalid email", 409 

            # Make sure the user is the loanee or loaner
            jwtId = get_jwt_identity()
            if not loanerUser.verify(jwtId) and not loaneeUser.verify(jwtId): 
                return "Error: Unauthortized", 401

            creatorId = jwtId
            newLoan = LoanModel(loanName, creatorId, loanerUser.id, loaneeUser.id, amount, interestRate, termMonths, startDate)
            dbSession.add(newLoan)
            dbSession.commit()
            return "success", 200
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

