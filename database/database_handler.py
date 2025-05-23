import sqlite3

class DatabaseHandler:
    def __init__(self, db_name='autorizados.db'):
        self.db_name = db_name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_name)
    
    def create_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorizados (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       tipo TEXT NOT NULL,
                       valor TEXT NOT NULL UNIQUE
                       )
        ''')
        conn.commit()
        conn.close()

    def add_autorizados(self, tipo, valor):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO autorizados (tipo, valor)
                VALUES (?, ?)  
            ''', (tipo, valor))
            conn.commit()
            print(f"{tipo.capitalize()} '{valor}' cadastrado com sucesso.")

        except sqlite3.IntegrityError:
            print(f"{tipo.capitalize()} '{valor}' já está cadastrado.")
        conn.close()

    def verificar_autorizado(self, tipo, valor):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM autorizados WHERE tipo = ? AND valor = ?
        ''', (tipo, valor))
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None
