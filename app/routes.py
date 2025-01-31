from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.forms import PlayerForm, MatchForm
from app.models import Player, Match, MatchPlayer
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('main', __name__)

def format_player_name(name, all_names):
    parts = name.split()
    first_name = parts[0]
    if len(parts) > 1:
        last_initial = parts[1][0]
        # Check if there are other players with the same first name
        same_first_name_count = sum(1 for n in all_names if n.split()[0] == first_name)
        if same_first_name_count > 1:
            return f"{first_name} {last_initial}."
    return first_name

@bp.app_template_filter('format_player_name')
def format_player_name_filter(name, all_names):
    return format_player_name(name, all_names)

@bp.route('/')
@login_required
def home():
    matches = Match.query.all()
    players = Player.query.all()
    player_names = [player.name for player in players]

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

    # Calculate the maximum number of pairings
    max_pairings = max(player_pairs.values(), default=0)

    return render_template(
        'index.html',
        total_matches=total_matches,
        wins=wins,
        losses=losses,
        draws=draws,
        team_stats=team_stats,
        player_match_count=player_match_count,
        player_pairs=player_pairs,
        max_pairings=max_pairings,
        players=players,
        player_names=player_names
    )

@bp.route('/players')
@login_required
def players():
    sort_by = request.args.get('sort_by', 'name')  # Default sorting by name
    order = request.args.get('order', 'asc')

    query = Player.query
    if sort_by in ['name', 'school']:
        if order == 'desc':
            query = query.order_by(getattr(Player, sort_by).desc())
        else:
            query = query.order_by(getattr(Player, sort_by).asc())

    players = query.all()
    return render_template('player_list.html', players=players, sort_by=sort_by, order=order)

@bp.route('/add_player', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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

@bp.route('/reports')
@login_required
def reports():
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
        'Smørås Lamborghini': Match.query.filter_by(team='Smørås Lamborghini').count()
    }

    # Player match participation statistics
    player_match_count = {}
    for match in matches:
        for player in match.players:
            player_match_count.setdefault(player.player.name, 0)
            player_match_count[player.player.name] += 1

    # Debug statements
    print(f"Total Matches: {total_matches}")
    print(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")
    print(f"Team Stats: {team_stats}")
    print(f"Player Match Count: {player_match_count}")

    return render_template(
        'reports.html',
        total_matches=total_matches,
        wins=wins,
        losses=losses,
        draws=draws,
        team_stats=team_stats,
        player_match_count=player_match_count
    )
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # Use hashed passwords in production
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))