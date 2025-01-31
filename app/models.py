from app import db
from flask_login import UserMixin

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    matches = db.relationship('MatchPlayer', backref='player', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Player {self.name} - {self.school}>'
    
class Match(db.Model):
    __tablename__ = 'match'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(50), nullable=False)
    players = db.relationship('MatchPlayer', backref='match', cascade="all, delete-orphan")
    result = db.Column(db.String(10), nullable=True)  # Add this line

class MatchPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)  # Fix syntax error

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))