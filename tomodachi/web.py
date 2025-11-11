"""Web interface for Tomodachi using Flask."""
from flask import Flask, render_template, jsonify, request
from pathlib import Path
from .pet import Pet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
# Always pick up template changes without restarting
app.config['TEMPLATES_AUTO_RELOAD'] = True
try:
    app.jinja_env.auto_reload = True
except Exception:
    pass

# Store pet in memory for demo (in production would use proper session/DB)
_pet = None

# Development mode: faster day progression toggle
_DEV_FAST_DAYS = False
_DEV_FAST_MULTIPLIER = 0.01  # 1% of real minutes -> 1440 * 0.01 = 14.4 minutes per day

def _apply_dev_day_length():
    from .pet import set_day_length_minutes
    if _DEV_FAST_DAYS:
        set_day_length_minutes(1440.0 * _DEV_FAST_MULTIPLIER)
    else:
        set_day_length_minutes(1440.0)

def get_pet():
    global _pet
    if _pet is None:
        _pet = Pet()
    return _pet

@app.route('/')
def index():
    """Render the main game page."""
    # Prevent browser caching so UI changes are visible immediately
    from flask import make_response
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/api/status')
def status():
    """Get current pet status."""
    pet = get_pet()
    # apply any dev day length override before ticking
    _apply_dev_day_length()
    pet.tick_realtime()
    return jsonify({
        'hunger': pet.hunger,
        'happiness': pet.happiness,
        'energy': pet.energy,
        'alive': pet.alive,
        'name': pet.name,
        'care_score': pet.care_score,
        'litter_dirt': pet.litter_dirt,
        'sick': pet.sick,
        'current_day': pet.current_day,
        'age_days': pet.current_day - pet.day_born,
        'max_age_days': pet.max_age_days
    })


@app.route('/api/dev/toggle_fast', methods=['POST'])
def toggle_fast_days():
    """Toggle developer fast-days mode (for quicker QA). Returns the new state."""
    global _DEV_FAST_DAYS
    data = request.get_json(force=True, silent=True) or {}
    # allow explicit state or toggle when no payload
    if 'enabled' in data:
        _DEV_FAST_DAYS = bool(data.get('enabled'))
    else:
        _DEV_FAST_DAYS = not _DEV_FAST_DAYS
    _apply_dev_day_length()
    return jsonify({'dev_fast_days': _DEV_FAST_DAYS})

@app.route('/api/feed')
def feed():
    """Feed the pet."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.feed(30)
    return jsonify({'status': 'ok'})

@app.route('/api/play')
def play():
    """Play with the pet."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    ok = pet.play(15)
    if not ok:
        return jsonify({'error': f'{pet.name} is too tired to play.'})
    return jsonify({'status': 'ok'})

@app.route('/api/sleep')
def sleep():
    """Let the pet sleep."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.sleep(3)
    return jsonify({'status': 'ok'})

@app.route('/api/clean')
def clean():
    """Clean the litter box."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.clean_litter()
    return jsonify({'status': 'ok'})

@app.route('/api/discipline')
def discipline():
    """Discipline the pet."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.discipline()
    return jsonify({'status': 'ok'})

@app.route('/api/attention')
def attention():
    """Give attention (petting) to the pet."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.give_attention()
    return jsonify({'status': 'ok'})

@app.route('/api/sickcare')
def sickcare():
    """Provide sick care to the pet."""
    pet = get_pet()
    pet.tick_realtime()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.sick_care()
    return jsonify({'status': 'ok'})

@app.route('/api/save', methods=['POST'])
def save():
    """Save pet state."""
    pet = get_pet()
    pet.tick_realtime()
    data = pet.to_dict()
    return jsonify(data)

@app.route('/api/load', methods=['POST'])
def load():
    """Load pet state."""
    global _pet
    data = request.get_json(force=True, silent=True) or {}
    _pet = Pet.from_dict(data)
    return jsonify({'status': 'ok'})

@app.route('/api/new', methods=['POST'])
def new_pet():
    """Create a new pet with the given name."""
    global _pet
    data = request.get_json(force=True, silent=True) or {}
    name = data.get('name', 'Tomo')
    _pet = Pet(name=name)
    _pet.tick_realtime()  # initialize timestamps
    return jsonify({'status': 'ok', 'name': name})

def run_web(host='127.0.0.1', port=5050, debug=False):
    """Run the web interface."""
    # Disable reloader so background process remains stable in this environment
    print(f"Tomodachi web server starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)