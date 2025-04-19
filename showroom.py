from flask import Flask, render_template, request, redirect, url_for
from database import Database

app = Flask(__name__)
db_handler = Database()

@app.before_request
def before_request():
    db_handler.connect()

@app.teardown_appcontext
def teardown_appcontext(exception):
    db_handler.close(exception)

@app.route('/')
def index():
    db = db_handler.connect()
    mobil_list = db.execute('SELECT * FROM mobil').fetchall()
    return render_template('index.html', mobil_list=mobil_list)

@app.route('/mobil/<int:id>')
def detail_mobil(id):
    db = db_handler.connect()
    mobil = db.execute('SELECT * FROM mobil WHERE id = ?', (id,)).fetchone()
    services = db.execute('SELECT * FROM service WHERE mobil_id = ?', (id,)).fetchall()
    total_service = sum([s['biaya'] for s in services])

    cicilan_bulanan = None
    hpp = mobil['harga_dasar'] + total_service
    if mobil['pinjaman_bank'] and mobil['suku_bunga']:
        bunga_total = mobil['pinjaman_bank'] * (mobil['suku_bunga'] / 100)
        total_pinjaman = mobil['pinjaman_bank'] + bunga_total
        cicilan_bulanan = total_pinjaman / 12
        hpp = (mobil['harga_dasar'] / (mobil['pinjaman_bank'] + mobil['suku_bunga'])) + total_service

    return render_template('detail_mobil.html', mobil=mobil, services=services, cicilan_bulanan=cicilan_bulanan, hpp=hpp, total_service=total_service)

@app.route('/tambah_mobil', methods=['GET', 'POST'])
def tambah_mobil():
    if request.method == 'POST':
        data = request.form
        db = db_handler.connect()
        db.execute('''
            INSERT INTO mobil (merk, model, tahun, harga_dasar, pinjaman_bank, suku_bunga)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['merk'], data['model'], int(data['tahun']),
            float(data['harga_dasar']),
            float(data['pinjaman_bank']) if data.get('pinjaman_bank') else None,
            float(data['suku_bunga']) if data.get('suku_bunga') else None
        ))
        db.commit()
        return redirect(url_for('index'))
    return render_template('tambah_mobil.html')

@app.route('/tambah_service/<int:mobil_id>', methods=['GET', 'POST'])
def tambah_service(mobil_id):
    if request.method == 'POST':
        data = request.form
        db = db_handler.connect()
        db.execute('''
            INSERT INTO service (mobil_id, tanggal, deskripsi, biaya)
            VALUES (?, ?, ?, ?)
        ''', (
            mobil_id,
            data['tanggal'],
            data['deskripsi'],
            float(data['biaya'])
        ))
        db.commit()
        return redirect(url_for('detail_mobil', id=mobil_id))
    return render_template('tambah_service.html', mobil_id=mobil_id)

@app.route('/hapus_mobil/<int:id>', methods=['POST'])
def hapus_mobil(id):
    db = db_handler.connect()
    db.execute('DELETE FROM service WHERE mobil_id = ?', (id,))
    db.execute('DELETE FROM mobil WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))