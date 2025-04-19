import sqlite3
from flask import g
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'showroom.db'))

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if 'db' not in g:
            g.db = sqlite3.connect(DB_PATH)
            g.db.row_factory = sqlite3.Row
        self.conn = g.db
        return self.conn

    def close(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init(self):
        db = self.connect()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS mobil (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merk TEXT NOT NULL,
                model TEXT NOT NULL,
                tahun INTEGER NOT NULL,
                harga_dasar REAL NOT NULL,
                pinjaman_bank REAL,
                suku_bunga REAL
            );

            CREATE TABLE IF NOT EXISTS service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobil_id INTEGER NOT NULL,
                tanggal TEXT NOT NULL,
                deskripsi TEXT NOT NULL,
                biaya REAL NOT NULL,
                FOREIGN KEY (mobil_id) REFERENCES mobil(id)
            );
        ''')
        db.commit()