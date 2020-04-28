Loan App

## Backend Overview
Backend is REST API build with python flask (flask-restful) and mySQL

## User authentication
1. User password is hashed and salted (with bcrypt) for secure databse storage and verification
2. Json web token (jwt) used to grant user access to endpoints once logged in