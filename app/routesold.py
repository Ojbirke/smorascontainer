from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.forms import PlayerForm, MatchForm
from app.models import Player, Match, MatchPlayer

bp = Blueprint('main', __name__)

def format_player_name(name):
    parts = name.split()
    if len(parts) > 1:
        return f"{parts[0]} {parts[1][0]}."
    return name

@bp.route('/')
def home():
    matches = Match.query.all()
    players = Player.query.all()

    # Calculate statistics
    total_matches = len(matches)
    wins = Match.query.filter_by(result='Win').count()
    losses = Match.query.filter_by(result='Loss').count()
    draws = Match.query.filter_by(result='Draw').count()
    
    # Team-wise statistics
    team_stats = {
        'Smørås Ferrari': Match.query.filter_by(team='Smørås Ferrari').count(),
        'Smørås Maserati': Match.query.filter_by(team='Smørås Maserati').count(),
        'Smørås Lamborghini': Match.query.filter_by(team='Smørås Lamborghini').count()  # Ensure the key exists
    }

    # Player match participation statistics
    player_match_count = {}
    player_pairs = defaultdict(int)
    for match in matches:
        players_in_match = [player.player.name for player in match.players]
        for player in match.players:
            player_match_count.setdefault(player.player.name, {
                'total': 0,
                'Smørås Ferrari': 0,
                'Smørås Maserati': 0,
                'Smørås Lamborghini': 0  # Ensure the key exists
            })
            player_match_count[player.player.name]['total'] += 1
            player_match_count[player.player.name].setdefault(match.team, 0)
            player_match_count[player.player.name][match.team] += 1

        # Calculate player pairs
        for i in range(len(players_in_match)):
            for j in range(i + 1, len(players_in_match)):
                player_pairs[(players_in_match[i], players_in_match[j])] += 1

    return render_template(
        'index.html',
        total_matches=total_matches,
        wins=wins,
        losses=losses,
        draws=draws,
        team_stats=team_stats,
        player_match_count=player_match_count,
        player_pairs=player_pairs,
        players=players
    )

@bp.route('/players')
def players():
    players = Player.query.all()
    return render_template('player_list.html', players=players)

@bp.route('/add_player', methods=['GET', 'POST'])
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        new_player = Player(
            name=form.name.data,
            school=form.school.data
        )
        db.session.add(new_player)
        db.session.commit()
        flash('Player added successfully!', 'success')
        return redirect(url_for('main.players'))
    return render_template('add_player.html', form=form)

@bp.route('/edit_player/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm(obj=player)
    if form.validate_on_submit():
        player.name = form.name.data
        player.school = form.school.data
        db.session.commit()
        flash('Player details updated!', 'success')
        return redirect(url_for('main.players'))
    return render_template('edit_player.html', form=form, player=player)

@bp.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash('Player deleted successfully!', 'danger')
    return redirect(url_for('main.players'))

@bp.route('/add_match', methods=['GET', 'POST'])
def add_match():
    form = MatchForm()
    form.players.choices = [(player.id, player.name) for player in Player.query.all()]
    
    if form.validate_on_submit():
        match = Match(
            date=form.date.data,
            time=form.time.data,
            opponent=form.opponent.data,
            team=form.team.data
        )
        db.session.add(match)
        db.session.commit()
        
        for player_id in form.players.data:
            match_player = MatchPlayer(match_id=match.id, player_id=player_id)
            db.session.add(match_player)
        
        db.session.commit()
        flash('Match added successfully!', 'success')
        return redirect(url_for('main.matches'))
    
    return render_template('add_match.html', form=form)

@bp.route('/matches', methods=['GET', 'POST'])
def matches():
    query = Match.query

    # Sorting functionality
    sort_by = request.args.get('sort_by', 'date')  # Default sorting by date
    order = request.args.get('order', 'asc')

    if sort_by in ['date', 'time', 'opponent', 'team', 'result']:
        if order == 'desc':
            query = query.order_by(getattr(Match, sort_by).desc())
        else:
            query = query.order_by(getattr(Match, sort_by).asc())

    matches = query.all()

    if request.method == 'POST':
        if 'match_id' in request.form:  # Updating match result
            match_id = request.form.get('match_id')
            new_result = request.form.get('result')
            match = Match.query.get_or_404(match_id)
            match.result = new_result
            db.session.commit()
            flash('Match result updated successfully!', 'success')

        elif 'delete_match_id' in request.form:  # Deleting match
            match_id = request.form.get('delete_match_id')
            match = Match.query.get_or_404(match_id)
            
            # Delete related player entries first to avoid foreign key constraint errors
            MatchPlayer.query.filter_by(match_id=match.id).delete()
            
            db.session.delete(match)
            db.session.commit()
            flash('Match deleted successfully!', 'danger')

        return redirect(url_for('main.matches'))

    return render_template('match_list.html', matches=matches)
