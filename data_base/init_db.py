import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('deb.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    nomenclature TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    fournisseur TEXT,
    article_id INTEGER,
    quantite INTEGER,
    montant_ht REAL,
    FOREIGN KEY(article_id) REFERENCES Articles(id)
)
''')

conn.commit()
conn.close()
