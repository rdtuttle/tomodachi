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
    pet.tick_realtime()
    return jsonify({
        'hunger': pet.hunger,
        'happiness': pet.happiness,
        'energy': pet.energy,
        'alive': pet.alive,
        'name': pet.name,
        'care_score': pet.care_score,
        'litter_dirt': pet.litter_dirt,
        'sick': pet.sick
    })

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

def run_web(host='127.0.0.1', port=5050, debug=False):
    """Run the web interface."""
    # Disable reloader so background process remains stable in this environment
    print(f"Tomodachi web server starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)