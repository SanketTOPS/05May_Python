import sqlite3
from fastapi import FastAPI


def DB_Connect():
    db=sqlite3.connect("stud.db")
    print("Database Created / Connected!")

DB_Connect()

app=FastAPI()

