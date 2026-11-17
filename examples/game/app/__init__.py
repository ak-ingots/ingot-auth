"""
The backend of the metagame of a game, the auth alone for now: the players
sign up, sign in and call with their token over gRPC, kept in MongoDB, their
attempts and sessions cached in Redis, their codes mailed by SMTP.
"""
