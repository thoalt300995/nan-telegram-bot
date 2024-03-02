import requests
import sqlite3
from sqlite3 import Error
import time
import threading
import concurrent.futures


# Connect to the SQLite Database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('namada.db')
    except Error as e:
        print(e)

    if conn:
        return conn


def close_connection(conn):
    conn.close()


# Create table
def create_table(conn):
    try:
        sql_create_ranking_table = """ CREATE TABLE IF NOT EXISTS ranking (
                                        id TEXT PRIMARY KEY UNIQUE,
                                        moniker TEXT NOT NULL,
                                        score INTEGER NOT NULL,
                                        ranking_position INTEGER NOT NULL,
                                        type TEXT NOT NULL
                                    );"""
        sql_create_user = """CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  validator text NOT NULL)"""
        c = conn.cursor()
        c.execute(sql_create_ranking_table)
        c.execute(sql_create_user)
    except Error as e:
        print(e)


# Save data to table
def save_ranking_table(conn, data):
    try:
        sql = ''' INSERT or REPLACE INTO ranking(id, moniker, score, ranking_position, type) VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)


def save_user_table(conn, data):
    try:
        sql = ''' INSERT OR REPLACE INTO users(id,validator) VALUES (?,?) '''
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)


# Get the Top 100 rankings by score
def get_player_by_number(conn, number, type):
    cur = conn.cursor()
    cur.execute("SELECT id,moniker,score,ranking_position FROM ranking where type=? ORDER BY score DESC LIMIT ?",
                (type, number,))
    return cur.fetchall()


# Get a player's data by ID
def get_player_by_id_or_moniker(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT id,moniker,score,ranking_position FROM ranking WHERE id=? or moniker=?", (id, id,))
    return cur.fetchall()


def get_all_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT id,validator FROM users")
    return cur.fetchall()


def get_user_by_validator(conn, validator):
    cur = conn.cursor()
    cur.execute("SELECT id FROM users where validator=?", (validator,))
    return cur.fetchall()


def get_user_by_id(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT validator FROM users where id=?", (id,))
    return cur.fetchall()


def delete_user(conn, id):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()

def main():
    conn = create_connection()
    create_table(conn)
    close_connection(conn)
