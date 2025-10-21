"""Web interface for Tomodachi using Flask."""
from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
from .pet import Pet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

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
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Get current pet status."""
    pet = get_pet()
    return jsonify({
        'hunger': pet.hunger,
        'happiness': pet.happiness,
        'energy': pet.energy,
        'alive': pet.alive,
        'name': pet.name,
        'care_score': pet.care_score
    })

@app.route('/api/feed')
def feed():
    """Feed the pet."""
    pet = get_pet()
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.feed(30)
    return jsonify({'status': 'ok'})

@app.route('/api/play')
def play():
    """Play with the pet."""
    pet = get_pet()
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
    if not pet.alive:
        return jsonify({'error': f'{pet.name} is no longer alive.'})
    pet.sleep(3)
    return jsonify({'status': 'ok'})

@app.route('/api/save', methods=['POST'])
def save():
    """Save pet state."""
    pet = get_pet()
    data = pet.to_dict()
    return jsonify(data)

@app.route('/api/load', methods=['POST'])
def load():
    """Load pet state."""
    global _pet
    data = request.json
    _pet = Pet.from_dict(data)
    return jsonify({'status': 'ok'})

def run_web(host='127.0.0.1', port=5000, debug=True):
    """Run the web interface."""
    app.run(host=host, port=port, debug=debug)