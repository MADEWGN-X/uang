from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
from deta import Deta
from datetime import datetime

app = Flask(__name__)
deta = Deta("c04gls7b4cl_sZ1SxsFRrpL3rzxJuoJJXpgefUhLvUCn")  # Ganti dengan API key deta Anda
db = deta.Base("uang")

def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(',', '.')

def kelompokkan_per_hari(catatan):
    data_per_hari = defaultdict(lambda: {'pemasukan': 0, 'pengeluaran': 0, 'saldo': 0, 'items': []})
    total_saldo = 0  # Inisialisasi total saldo
    for item in catatan:
        tanggal = item['tanggal']
        jumlah = item['jumlah']
        if jumlah >= 0:
            data_per_hari[tanggal]['pemasukan'] += jumlah
        else:
            data_per_hari[tanggal]['pengeluaran'] += abs(jumlah)
        data_per_hari[tanggal]['items'].append(item)
        
    # Hitung saldo per hari dan total saldo
    for data in data_per_hari.values():
        data['saldo'] = data['pemasukan'] - data['pengeluaran']
        total_saldo += data['saldo']

    return data_per_hari, total_saldo

def dapatkan_semua_catatan():
    return db.fetch().items

@app.route('/')
def index():
    catatan = dapatkan_semua_catatan()
    data_per_hari, total_saldo = kelompokkan_per_hari(catatan)
    return render_template('index.html', data_per_hari=data_per_hari, total_saldo=total_saldo, format_rupiah=format_rupiah)

@app.route('/tambah-pemasukan', methods=['POST'])
def tambah_pemasukan():
    jumlah = request.form['jumlah']
    keterangan = request.form['keterangan']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    db.put({"jumlah": float(jumlah), "keterangan": keterangan, "tanggal": tanggal})
    return redirect(url_for('index'))

@app.route('/tambah-pengeluaran', methods=['POST'])
def tambah_pengeluaran():
    jumlah = request.form['jumlah']
    keterangan = request.form['keterangan']
    tanggal = datetime.now().strftime('%Y-%m-%d')
    db.put({"jumlah": -float(jumlah), "keterangan": keterangan, "tanggal": tanggal})
    return redirect(url_for('index'))

@app.route('/hapus/<key>', methods=['POST'])
def hapus(key):
    db.delete(key)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
