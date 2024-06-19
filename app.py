from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
import sqlite3
import csv
import os

app = Flask(__name__)

DATABASE = 'deb.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                nomenclature TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                fournisseur TEXT NOT NULL,
                article_id INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                montant_ht REAL NOT NULL,
                nc8 TEXT NOT NULL,
                ngp9 TEXT,
                pays_origine TEXT,
                valeur REAL,
                regime TEXT,
                masse_nette REAL,
                unites_suppl REAL,
                nature_transaction_a TEXT,
                nature_transaction_b TEXT,
                mode_transport TEXT,
                departement TEXT,
                pays_provenance TEXT,
                code_tva TEXT,
                reference_interne TEXT,
                FOREIGN KEY (article_id) REFERENCES Articles (id)
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Articles')
    articles = cursor.fetchall()
    conn.close()
    return render_template('index.html', articles=articles)

@app.route('/add_article', methods=['POST'])
def add_article():
    nom = request.form['nom']
    nomenclature = request.form['nomenclature']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Articles (nom, nomenclature) VALUES (?, ?)', (nom, nomenclature))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_facture', methods=['POST'])
def add_facture():
    date = request.form['date']
    fournisseur = request.form['fournisseur']
    article_id = request.form['article_id']
    quantite = request.form['quantite']
    montant_ht = request.form['montant_ht']
    nc8 = request.form['nc8']
    ngp9 = request.form['ngp9']
    pays_origine = request.form['pays_origine']
    valeur = request.form['valeur']
    regime = request.form['regime']
    masse_nette = request.form['masse_nette']
    unites_suppl = request.form['unites_suppl']
    nature_transaction_a = request.form['nature_transaction_a']
    nature_transaction_b = request.form['nature_transaction_b']
    mode_transport = request.form['mode_transport']
    departement = request.form['departement']
    pays_provenance = request.form['pays_provenance']
    code_tva = request.form['code_tva']
    reference_interne = request.form['reference_interne']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Factures (
            date, fournisseur, article_id, quantite, montant_ht, nc8, ngp9, pays_origine, valeur,
            regime, masse_nette, unites_suppl, nature_transaction_a, nature_transaction_b, mode_transport,
            departement, pays_provenance, code_tva, reference_interne
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, fournisseur, article_id, quantite, montant_ht, nc8, ngp9, pays_origine, valeur, regime,
          masse_nette, unites_suppl, nature_transaction_a, nature_transaction_b, mode_transport,
          departement, pays_provenance, code_tva, reference_interne))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files['file']
    if not file:
        return 'No file uploaded', 400

    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    with open(filepath, newline='', encoding='latin1') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        next(csvreader)  # Skip the header row
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        for row in csvreader:
            cursor.execute('INSERT INTO Articles (nom, nomenclature) VALUES (?, ?)', (row[0], row[1]))
        conn.commit()
        conn.close()

    os.remove(filepath)
    return redirect(url_for('index'))

@app.route('/search_article', methods=['GET'])
def search_article():
    query = request.args.get('query', '')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Articles WHERE nom LIKE ?', ('%' + query + '%',))
    articles = cursor.fetchall()
    conn.close()
    return jsonify(articles)

@app.route('/generate_csv')
def generate_csv():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Factures')
    factures = cursor.fetchall()

    with open('deb_export.csv', 'w', newline='', encoding='latin1') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';')
        csvwriter.writerow([
            'Nomenclature (NC8)', 'NGP9', 'Pays d\'origine / Pays de destination', 'Valeur', 'Régime',
            'Masse Nette', 'Unités supplémentaires', 'Nature de la transaction A', 'Nature de la transaction B',
            'Mode de Transport', 'Département', 'Pays de Provenance / Pays d\'origine', 'Code TVA Partenaire étranger',
            'Référence interne'
        ])
        for facture in factures:
            csvwriter.writerow([
                facture[6], facture[7], facture[8], facture[9], facture[10], facture[11], facture[12],
                facture[13], facture[14], facture[15], facture[16], facture[17], facture[18], facture[19]
            ])

    conn.close()
    return send_file('deb_export.csv', as_attachment=True, download_name='deb_export.csv')

if __name__ == '__main__':
    init_db()
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files['file']
    if not file:
        return 'No file uploaded', 400

    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    with open(filepath, newline='', encoding='latin1') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        next(csvreader)  # Skip the header row
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        for row in csvreader:
            cursor.execute('SELECT * FROM Articles WHERE nom = ? AND nomenclature = ?', (row[0], row[1]))
            data = cursor.fetchone()
            if data is None:
                cursor.execute('INSERT INTO Articles (nom, nomenclature) VALUES (?, ?)', (row[0], row[1]))
        conn.commit()
        conn.close()

    os.remove(filepath)
    return redirect(url_for('index'))
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                nomenclature TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                fournisseur_id INTEGER NOT NULL,
                article_id INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                montant_ht REAL NOT NULL,
                nc8 TEXT NOT NULL,
                ngp9 TEXT,
                pays_origine TEXT,
                valeur REAL,
                regime TEXT,
                masse_nette REAL,
                unites_suppl REAL,
                nature_transaction_a TEXT,
                nature_transaction_b TEXT,
                mode_transport TEXT,
                departement TEXT,
                pays_provenance TEXT,
                code_tva TEXT,
                reference_interne TEXT,
                FOREIGN KEY (article_id) REFERENCES Articles (id),
                FOREIGN KEY (fournisseur_id) REFERENCES Fournisseurs (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Fournisseurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                pays_origine TEXT,
                nature_transaction TEXT
            )
        ''')
        conn.commit()
@app.route('/add_facture', methods=['POST'])
def add_facture():
    date = request.form['date']
    fournisseur = request.form['fournisseur']
    article_id = request.form['article_id']
    quantite = request.form['quantite']
    montant_ht = request.form['montant_ht']
    nc8 = request.form['nc8']
    ngp9 = request.form['ngp9']
    pays_origine = request.form['pays_origine']
    valeur = request.form['valeur']
    regime = request.form['regime']
    masse_nette = request.form['masse_nette']
    unites_suppl = request.form['unites_suppl']
    nature_transaction_a = request.form['nature_transaction_a']
    nature_transaction_b = request.form['nature_transaction_b']
    mode_transport = request.form['mode_transport']
    departement = request.form['departement']
    pays_provenance = request.form['pays_provenance']
    code_tva = request.form['code_tva']
    reference_interne = request.form['reference_interne']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Fournisseurs WHERE nom = ?', (fournisseur,))
    fournisseur_data = cursor.fetchone()
    if fournisseur_data is None:
        cursor.execute('INSERT INTO Fournisseurs (nom, pays_origine, nature_transaction) VALUES (?, ?, ?)', 
                       (fournisseur, pays_origine, nature_transaction_a))
        fournisseur_id = cursor.lastrowid
    else:
        fournisseur_id = fournisseur_data[0]
        cursor.execute('UPDATE Fournisseurs SET pays_origine = ?, nature_transaction = ? WHERE id = ?', 
                       (pays_origine, nature_transaction_a, fournisseur_id))

    cursor.execute('''
        INSERT INTO Factures (
            date, fournisseur_id, article_id, quantite, montant_ht, nc8, ngp9, pays_origine, valeur,
            regime, masse_nette, unites_suppl, nature_transaction_a, nature_transaction_b, mode_transport,
            departement, pays_provenance, code_tva, reference_interne
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, fournisseur_id, article_id, quantite, montant_ht, nc8, ngp9, pays_origine, valeur, regime,
          masse_nette, unites_suppl, nature_transaction_a, nature_transaction_b, mode_transport,
          departement, pays_provenance, code_tva, reference_interne))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
