from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Medico(db.Model):
    __tablename__ = "medicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    especialidade = db.Column(db.String(100), nullable=False)
    crm = db.Column(db.String(50), unique=True, nullable=False)  # Conselho Regional de Medicina
    senha_hash = db.Column(db.String(255), nullable=False)

    # Dados adicionais
    hospital = db.Column(db.String(120), nullable=True)
    disponibilidade = db.Column(db.String(255), nullable=True)  # Ex: "Seg-Sex 8h-18h"
    criado_em = db.Column(db.DateTime, server_default=db.func.now())
    atualizado_em = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f"<Medico {self.nome} - {self.especialidade}>"
