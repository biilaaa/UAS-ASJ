import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Film(db.Model):
    __tablename__ = 'listFilm'  # 👈 tambahkan ini agar cocok dengan nama tabel di MySQL
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100), nullable=False)
    sutradara = db.Column(db.String(100), nullable=False)
    tahun = db.Column(db.String(10), nullable=False)


@app.route('/')
def index():
    film_list = Film.query.all()
    return render_template('index.html', film_list=film_list)

@app.route('/add', methods=['GET', 'POST'])
def add_film():
    if request.method == 'POST':
        film = Film(
            judul=request.form['judul'],
            sutradara=request.form['sutradara'],
            tahun=request.form['tahun']
        )
        db.session.add(film)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_film(id):
    film = Film.query.get_or_404(id)
    if request.method == 'POST':
        film.judul = request.form['judul']
        film.sutradara = request.form['sutradara']
        film.tahun = request.form['tahun']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', film=film)

@app.route('/delete/<int:id>')
def delete_film(id):
    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/film', methods=['GET', 'POST'])
def handle_film():
    if request.method == 'POST':
        data = request.get_json()
        film = Film(judul=data['judul'], sutradara=data['sutradara'], tahun=data['tahun'])
        db.session.add(film)
        db.session.commit()
        return jsonify({"message": "Film ditambahkan", "data": data}), 201

    films = Film.query.all()
    result = [{"id": f.id, "judul": f.judul, "sutradara": f.sutradara, "tahun": f.tahun} for f in films]
    return jsonify(result)

@app.route('/film/<int:id>', methods=['PUT', 'DELETE'])
def handle_film_detail(id):
    film = Film.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.get_json()
        film.judul = data.get('judul', film.judul)
        film.sutradara = data.get('sutradara', film.sutradara)
        film.tahun = data.get('tahun', film.tahun)
        db.session.commit()
        return jsonify({"message": "Data film diupdate"})
    elif request.method == 'DELETE':
        db.session.delete(film)
        db.session.commit()
        return jsonify({"message": "Film dihapus"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
