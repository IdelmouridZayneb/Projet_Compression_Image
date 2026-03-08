from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/analyser', methods=['POST'])
def analyser():
    data = request.get_json()
    image_path = data.get('image_path', '')
    if not image_path:
        return jsonify({'erreur': 'image_path manquant'}), 400
    chemin = f'database-projet/{image_path}'
    if not os.path.exists(chemin):
        return jsonify({'erreur': f'Image introuvable : {chemin}'}), 404
    result = subprocess.run(
        [r'C:\Users\ELITEBOOK\anaconda3\python.exe', r'D:\agent_analyse_sara.py', chemin],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        output = json.loads(result.stdout)
        return jsonify(output)
    else:
        return jsonify({'erreur': result.stderr}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'Agent Analyse Sara actif !'})

if __name__ == '__main__':
    print('🚀 Serveur Agent Analyse Sara - http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
