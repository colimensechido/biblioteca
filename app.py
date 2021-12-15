
from flask import Flask, render_template, redirect, request
from flask.templating import render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from sqlalchemy.orm import create_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/catalogo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'xd'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

###MODELOS
class Usuarios(UserMixin, db.Model):
    __tablename__= "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email=email
        self.password=password

class Editorial(db.Model):
    __tablaname__ = "editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial=nombre_editorial
    
class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)
    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, id_editorial, id_autor, id_genero):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.id_editorial = id_editorial
        self.id_autor = id_autor
        self.id_genero = id_genero


class Autor(db.Model):
    __tablaname__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(80))
    fecha_nac = db.Column(db.Date)
    nacionaliad = db.Column(db.String(40))

    def __init__(self, nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionaliad = nacionalidad

class Genero(db.Model):
    __tablaname__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(80))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero


class MisFavoritos(db.Model):
    __tablaname__ = "misfavoritos"
    id_lista_favoritos = db.Column(db.Integer, primary_key=True)
    
    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    def __init__(self, id_libro , id_usuario):
        self.id_libro  = id_libro 
        self.id_usuario = id_usuario

       

@app.route("/")
def index():
    return render_template("index.html")
#------------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(userid):
    return Usuarios.query.get(int(userid))


@app.route("/iniciarsesion")
def loginn():
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/login", methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    consulta_usuario = Usuarios.query.filter_by(email=email).first()
    password_cifrado = bcrypt.check_password_hash(consulta_usuario.password,password)
    

    if bcrypt.check_password_hash(consulta_usuario.password,password) == password_cifrado:
        login_user(consulta_usuario)
        return redirect("/")
    else:
        return redirect("/")


@app.route("/registrar")
def registrar():
    return render_template("registrar.html")

@app.route("/registrar_usuario", methods=['POST'])
def registrar_usuario():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    password_cifrado = bcrypt.generate_password_hash(password).decode('utf-8')
    usuario = Usuarios(email = email, password=password_cifrado)
    db.session.add(usuario)
    db.session.commit()
    return redirect("/iniciarsesion")
 

#libros ---------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/catalogo")
@login_required
def catalogo():
    Libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Genero.nombre_genero, Libro.titulo_libro, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial, Libro.volumen, Libro.fecha_publicacion, Libro.id_libro)
    return render_template("libros/catalogo.html", libro = Libros)

@app.route("/addbook")
@login_required
def registrar_libro():
    autorConsulta = Autor.query.all()
    generoConsulta = Genero.query.all()
    editorialConsulta = Editorial.query.all()
    return render_template("libros/agregarLibro.html", autores = autorConsulta, generos = generoConsulta, editoriales = editorialConsulta)
@app.route("/add_book", methods=["POST"])
@login_required
def registrarlibro():
    nombreLibro = request.form["nombreLibro"]
    paginas = request.form["paginas"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    fechaPublic = request.form["fecha"]
    formato = request.form["formato"]
    genero = request.form["genero"]
    autor = request.form["autor"]
    libro = Libro(titulo_libro=nombreLibro, fecha_publicacion=fechaPublic, numero_paginas=paginas, formato=formato, volumen=volumen, id_editorial=editorial, id_genero=genero, id_autor=autor)
    db.session.add(libro)
    db.session.commit()
    return redirect("/")

@app.route("/editbook/<id>")
@login_required
def editbook(id):
    libro = Libro.query.filter_by(id_libro = int(id)).first()
    genero = Genero.query.all()
    autor = Autor.query.all()
    editorial = Editorial.query.all()
    formato = ["1","2"]
    return render_template("libros/modificarLibro.html", libros = libro, generos = genero, autores = autor, editoriales = editorial, format = formato)

@app.route("/edit_book", methods=["POST"])
@login_required
def edit_book():
    idlibro = request.form["idlibro"]
    nombreLibro = request.form["nombreLibro"]
    paginas = request.form["paginas"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    fechaPublic = request.form["fecha"]
    formato = request.form["formato"]
    genero = request.form["genero"]
    autor = request.form["autor"]

    libro = Libro.query.filter_by(id_libro=int(idlibro)).first()
    libro.titulo_libro = nombreLibro
    libro.fecha_publicacion = fechaPublic
    libro.numero_paginas = paginas
    libro.volumen = volumen
    libro.id_editorial = editorial
    libro.id_genero = genero
    libro.formato = formato
    libro.id_autor = autor
    db.session.commit()
    return redirect("/catalogo")

@app.route("/deletebook/<id>")
@login_required
def deletebook(id):
    libro = Libro.query.filter_by(id_libro = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo")


#libros ---------------------------------------------------------------------------------------------------------------------------------------------------------

#autores ---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/catalogo_autores")
@login_required
def catalogo_autores():
    autores = Autor.query.all()
    return render_template("autores/autores.html", autores = autores)

@app.route("/addautor")
@login_required
def registrar_autor():
    return render_template("autores/agregarAutor.html")

@app.route("/add_autor", methods=["POST"])
@login_required
def registrarAutor():
    nombreA = request.form["nombreAutor"]
    fechaN = request.form["FeNac"]
    nac = request.form["nacionalidad"]
    autor = Autor(nombre_autor = nombreA, fecha_nac = fechaN, nacionalidad = nac )
    db.session.add(autor)
    db.session.commit()

    return redirect("/catalogo_autores")

@app.route("/deleteautor/<id>")
@login_required
def deleteautor(id):
    autor = Autor.query.filter_by(id_autor = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_autores")


@app.route("/editautor/<id>")
@login_required
def editautor(id):
    autor = Autor.query.filter_by(id_autor = int(id)).first()
    return render_template("autores/modificarAutor.html", autores = autor)

@app.route("/edit_autor", methods=["POST"])
@login_required
def edit_autor():
    idautor = request.form["idautor"]
    nombreA = request.form["nombreAutor"]
    fechaN = request.form["FeNac"]
    nac = request.form["nacionalidad"]
    
    autor = Autor.query.filter_by(id_autor=int(idautor)).first()
    autor.nombre_autor = nombreA
    autor.fecha_nac = fechaN
    autor.nacionalidad = nac
    db.session.commit()
    return redirect("/catalogo_autores")



#autores ---------------------------------------------------------------------------------------------------------------------------------------------------------
    
#generos ---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/catalogo_generos")
@login_required
def catalogo_generos():
    generos = Genero.query.all()
    return render_template("generos/generos.html", generos = generos)

@app.route("/addgenero")
@login_required
def registrogenero():
    return render_template("generos/agregarGenero.html")

@app.route("/add_genero", methods=["POST"])
@login_required

def registrargenero():
    nombreG = request.form["nombreGenero"]

    genero = Genero(nombre_genero = nombreG)
    db.session.add(genero)
    db.session.commit()

    return redirect("/catalogo_generos")

@app.route("/editgenero/<id>")
@login_required
def editgenero(id):
    genero = Genero.query.filter_by(id_genero = int(id)).first()
    return render_template("generos/modificarGenero.html", generos = genero)

@app.route("/edit_genero", methods=["POST"])
@login_required
def edit_genero():
    idgenero = request.form["idgenero"]
    nombreG = request.form["nombreG"]
    
    genero = Genero.query.filter_by(id_genero=int(idgenero)).first()
    genero.nombre_genero = nombreG
    db.session.commit()
    return redirect("/catalogo_generos")


@app.route("/deletegenero/<id>")
@login_required
def deletegenero(id):
    genero = Genero.query.filter_by(id_genero = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_generos")
#generos ---------------------------------------------------------------------------------------------------------------------------------------------------------

#editoriales ---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/catalogo_editoriales")
@login_required
def catalogo_editoriales():
    editoriales = Editorial.query.all()
    return render_template("editoriales/editoriales.html", editoriales = editoriales)

@app.route("/addeditorial")
@login_required
def agregarEditorial():
    return render_template("editoriales/agregarEditorial.html")

@app.route("/add_editorial", methods=["POST"])
@login_required
def registrareditorial():
    nombreE = request.form["nombreEditorial"]

    editorial = Editorial(nombre_editorial= nombreE)
    db.session.add(editorial)
    db.session.commit()

    return redirect("/")

@app.route("/editeditorial/<id>")
@login_required
def editeditorial(id):
    editorial = Editorial.query.filter_by(id_editorial = int(id)).first()
    return render_template("editoriales/modificarEditorial.html", editoriales = editorial)

@app.route("/edit_editorial", methods=["POST"])
@login_required
def edit_editorial():
    ideditorial = request.form["ideditorial"]
    nombreE = request.form["nombreE"]
    
    editorial = Editorial.query.filter_by(id_editorial=int(ideditorial)).first()
    editorial.nombre_editorial = nombreE
    db.session.commit()
    return redirect("/catalogo_editoriales")


@app.route("/deleteeditorial/<id>")
@login_required
def deleteeditorial(id):
    editorial = Editorial.query.filter_by(id_editorial = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_editoriales")

#editoriales ---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/favoritos")
@login_required
def favoritos():
    Libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).join(MisFavoritos, Libro.id_libro == MisFavoritos.id_libro).add_columns(Genero.nombre_genero, Libro.titulo_libro, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial, Libro.fecha_publicacion, Libro.volumen, Libro.id_libro, MisFavoritos.id_usuario, MisFavoritos.id_lista_favoritos)
    return render_template("favoritos.html", iduser = current_user.id, libros = Libros)

@app.route("/addfav/<id>")
@login_required
def addfav(id):
    favorito = MisFavoritos(id_libro=id,id_usuario=current_user.id)
    db.session.add(favorito)
    db.session.commit()
    return redirect("/catalogo")

@app.route("/deletefav/<id>")
@login_required
def delfav(id):
    fav = MisFavoritos.query.filter_by(id_lista_favoritos = int (id)).delete()
    db.session.commit()
    return redirect("/favoritos")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    
