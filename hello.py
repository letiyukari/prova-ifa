import os
from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Definindo o diretório base para o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando as extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definição da classe Role
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    occurrences = db.relationship('Occurrence', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

# Definição da classe Occurrence
class Occurrence(db.Model):
    __tablename__ = 'occurrences'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    date = db.Column(db.DateTime)  # Alterando para DateTime
    description = db.Column(db.String(250))

    def __repr__(self):
        return f'<Occurrence {self.description}>'

# Formulário para adicionar uma ocorrência
class OccurrenceForm(FlaskForm):
    role = SelectField('Disciplina Associada:', choices=[
        ('DSWA5', 'DSWA5'),
        ('GPSA5', 'GPSA5'),
        ('IHCA5', 'IHCA5'),
        ('SODA5', 'SODA5'),
        ('PJIA5', 'PJIA5'),
        ('TCOA5', 'TCOA5')
    ], validators=[DataRequired()])

    date = DateTimeLocalField('Data da Ocorrência:', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Descrição da Ocorrência (250 caracteres):', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

# Shell context
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, Occurrence=Occurrence)

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Página principal
@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

# Página para cadastrar e listar ocorrências
@app.route('/ocorrencias', methods=['GET', 'POST'])
def ocorrencias():
    form = OccurrenceForm()

    # Buscando todas as ocorrências para exibição
    occurrences_all = Occurrence.query.order_by(Occurrence.date.desc()).all()
    occurrences_count = Occurrence.query.count()

    # Verificando se o formulário foi submetido
    if form.validate_on_submit():
        # Criando a nova ocorrência
        occurrence = Occurrence(
            role=form.role.data,
            date=form.date.data,
            description=form.description.data
        )
        db.session.add(occurrence)
        db.session.commit()

        flash('Ocorrência cadastrada com sucesso!')
        return redirect(url_for('ocorrencias'))

    # Renderizando o template com o formulário e as ocorrências
    return render_template('ocorrencias.html', form=form, occurrences_all=occurrences_all, occurrences_count=occurrences_count)


# Página de indisponibilidade
@app.route('/naodisponivel')
def naodisponivel():
    current_time = datetime.now()
    return render_template('naodisponivel.html', current_time=current_time)

# Rodando a aplicação
if __name__ == '__main__':
    app.run(debug=True)
