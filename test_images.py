"""
Script de Test Automatique - 30 Images
Ordre correct : Analyste → Décideur → Comparateur → Exécuteur → Rapporteur
Déclenché par n8n via Webhook sur port 5001
Lance avec: python test_images.py
"""

import requests
import json
import os
import time
import re
import threading
from pathlib import Path
from flask import Flask, request, jsonify

# ============================================================
# CONFIGURATION
# ============================================================
SERVER_URL   = "http://127.0.0.1:5000"
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"
WEBHOOK_PORT = 5001

# ⚠️ CORRECTION : Utiliser le même chemin que dans app_presentation.py
IMAGES_ROOT  = r"C:\Users\Lenovo ThinkPad T470\OneDrive\Documents\Bureau\Projet_Compression\images_test"
RAPPORTS_DIR = r"C:\Users\Lenovo ThinkPad T470\OneDrive\Documents\Bureau\Projet_Compression\rapports"

# ============================================================
# FLASK WEBHOOK
# ============================================================
webhook_app = Flask(__name__)

@webhook_app.route('/lancer-tests', methods=['POST'])
def lancer_tests():
    data    = request.json or {}
    dossier = data.get("dossier", "tous")
    print(f"\n🚀 Signal reçu de n8n ! Dossier : {dossier}")
    thread = threading.Thread(target=lancer_pipeline, args=(dossier,))
    thread.daemon = True
    thread.start()
    return jsonify({
        "status" : "lancé",
        "message": f"Tests démarrés pour : {dossier}",
        "webhook": f"http://127.0.0.1:{WEBHOOK_PORT}/lancer-tests"
    })

@webhook_app.route('/resultats', methods=['GET'])
def voir_resultats():
    resume_path = os.path.join(RAPPORTS_DIR, "resume_global.json")
    if os.path.exists(resume_path):
        with open(resume_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({"message": "Aucun résultat disponible"})

@webhook_app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status"  : "running",
        "port"    : WEBHOOK_PORT,
        "endpoints": {
            "lancer"   : "POST /lancer-tests",
            "resultats": "GET  /resultats"
        }
    })

# ============================================================
# AGENT DÉCIDEUR — Ollama
# ============================================================
def agent_decideur_ollama(features):
    prompt = f"""Tu es un expert en compression d'images.

Caracteristiques de l'image :
- Type      : {features.get('image_type','?')}
- Resolution: {features.get('resolution',{}).get('width','?')}x{features.get('resolution',{}).get('height','?')}
- Entropie  : {features.get('entropy','?')}
- Contours  : {features.get('edge_density','?')}
- Taille    : {features.get('file_size_kb','?')} Ko

Reponds UNIQUEMENT avec ce JSON (rien d'autre) :
{{"format": "JPEG", "quality": 85, "justification": "raison courte"}}

Formats : JPEG, PNG, WEBP. Quality entre 60 et 95."""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120
        )
        texte = r.json().get("response", "")
        match = re.search(r'\{[\s\S]*?\}', texte)
        if match:
            parsed = json.loads(match.group(0))
            return {
                "format"       : parsed.get("format", "WEBP"),
                "quality"      : int(parsed.get("quality", 85)),
                "justification": parsed.get("justification", "")[:200],
                "source"       : f"Ollama {OLLAMA_MODEL}"
            }
    except Exception:
        pass
    return decision_locale(features)

def decision_locale(features):
    image_type = features.get("image_type", "photo_standard")
    regles = {
        "document_texte"     : ("PNG",  90, "Document → PNG sans perte"),
        "image_simple_logo"  : ("PNG",  90, "Logo → PNG couleurs plates"),
        "photo_complexe"     : ("JPEG", 85, "Photo complexe → JPEG"),
        "graphique_diagramme": ("WEBP", 85, "Graphique → WebP"),
        "photo_standard"     : ("WEBP", 85, "Photo standard → WebP"),
    }
    fmt, qual, just = regles.get(image_type, ("WEBP", 85, "Par défaut"))
    return {"format": fmt, "quality": qual, "justification": just, "source": "règles locales"}

# ============================================================
# APPEL GÉNÉRIQUE AUX AGENTS
# ============================================================
def appeler(endpoint, data, timeout=60):
    try:
        r = requests.post(f"{SERVER_URL}/{endpoint}", json=data, timeout=timeout)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# PIPELINE POUR UNE IMAGE
# Ordre : Analyste → Décideur → Comparateur → Exécuteur → Rapporteur
# ============================================================
def tester_image(image_path, categorie, nom_image):
    print(f"\n  📸 {nom_image} ({categorie})")
    rapport = {"image": nom_image, "categorie": categorie, "chemin": image_path}

    # ── 1. ANALYSTE ──
    r1 = appeler("agent/analyste", {"image_path": image_path})
    if "error" in r1:
        print(f"     ❌ Analyste : {r1['error']}")
        rapport["erreur"] = r1['error']
        return rapport
    features = r1.get("features", {})
    print(f"     ✅ Analyste → type={features.get('type_image')} | entropie={features.get('features_statistiques', {}).get('entropy')}")
    rapport["analyse"] = features

    # ── 2. DÉCIDEUR (Ollama) ──
    decision = agent_decideur_ollama({
        "image_type": features.get("type_image"),
        "resolution": {
            "width": features.get("metadonnees", {}).get("largeur"),
            "height": features.get("metadonnees", {}).get("hauteur")
        },
        "entropy": features.get("features_statistiques", {}).get("entropy"),
        "edge_density": features.get("contours", {}).get("nombre_contours"),
        "file_size_kb": features.get("metadonnees", {}).get("taille_kb")
    })
    print(f"     ✅ Décideur → {decision.get('format')} q={decision.get('quality')} ({decision.get('source')})")
    rapport["decision_initiale"] = decision

    # ── 3. COMPARATEUR (valide/corrige la décision AVANT compression) ──
    rc = appeler("agent/comparateur", {
        "image_path"  : image_path,
        "llm_decision": decision,
        "features"    : features
    }, timeout=120)

    if "error" not in rc:
        decision_finale  = rc.get("meilleure_decision", decision)
        decision_changee = rc.get("decision_changee", False)
        rapport["comparaison_strategies"] = rc.get("strategies_testees", {})
        print(f"     ✅ Comparateur → décision {'✓ confirmée' if not decision_changee else '✗ corrigée : ' + decision_finale.get('format','?')}")
    else:
        decision_finale  = decision
        decision_changee = False
        print(f"     ⚠️ Comparateur échoué → on garde décision LLM")
    rapport["decision_finale"] = decision_finale

    # ── 4. EXÉCUTEUR (applique la décision validée) ──
    r3 = appeler("agent/executeur", {
        "image_path": image_path,
        "format"    : decision_finale.get("format", "WEBP"),
        "quality"   : decision_finale.get("quality", 85),
        "ssim_min"  : 0.85
    }, timeout=120)

    if "error" in r3:
        print(f"     ❌ Exécuteur : {r3['error']}")
        rapport["erreur"] = r3['error']
        return rapport

    metrics = r3.get("metrics", {})
    print(f"     ✅ Exécuteur → PSNR={metrics.get('psnr_db')}dB | SSIM={metrics.get('ssim')} | τ={metrics.get('taux_compression_pct')}%")
    rapport["metriques"] = metrics

    # ── 5. RAPPORTEUR ──
    metrics_rapport = {
        **metrics,
        "format_used" : decision_finale.get("format", "WEBP"),
        "quality_used": decision_finale.get("quality", 85)
    }
    r4 = appeler("agent/rapporteur", {
        "features"    : features,
        "llm_decision": decision_finale,
        "metrics"     : metrics_rapport
    })
    if "error" not in r4:
        conclusion = r4.get("rapport", {}).get("rapport_compression", {}).get("conclusion", "")
        print(f"     ✅ Rapporteur → {conclusion}")
        rapport["rapport_final"] = r4.get("rapport", {})

    rapport["decision_changee_par_comparateur"] = decision_changee
    return rapport

# ============================================================
# PIPELINE COMPLET
# ============================================================
def lancer_pipeline(dossier_filtre="tous"):
    os.makedirs(RAPPORTS_DIR, exist_ok=True)
    for cat in ['photos', 'documents', 'graphiques', 'screenshots']:
        os.makedirs(os.path.join(RAPPORTS_DIR, cat), exist_ok=True)

    extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    images     = []

    # ⚠️ CORRECTION : Utiliser les mêmes noms de catégories
    categories = ['photos', 'documents', 'graphiques', 'screenshots'] \
                 if dossier_filtre == "tous" else [dossier_filtre]

    for categorie in categories:
        dossier = os.path.join(IMAGES_ROOT, categorie)
        if not os.path.exists(dossier):
            print(f"  ⚠️ Dossier manquant : {dossier}")
            continue
        for fichier in sorted(os.listdir(dossier)):
            if Path(fichier).suffix.lower() in extensions:
                images.append({
                    "path"     : os.path.join(dossier, fichier),
                    "categorie": categorie,
                    "nom"      : fichier
                })

    print(f"\n📁 {len(images)} images trouvées\n")

    resultats = []
    nb_succes = nb_erreurs = 0
    debut     = time.time()

    for i, img in enumerate(images, 1):
        print(f"[{i}/{len(images)}]", end=" ")
        rapport = tester_image(img["path"], img["categorie"], img["nom"])

        if "erreur" not in rapport:
            nb_succes += 1
            nom_f  = img["nom"].replace('.', '_') + '_rapport.json'
            path_r = os.path.join(RAPPORTS_DIR, img["categorie"], nom_f)
            with open(path_r, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, indent=2, ensure_ascii=False)
        else:
            nb_erreurs += 1

        resultats.append({
            "image"            : img["nom"],
            "categorie"        : img["categorie"],
            "type_detecte"     : rapport.get("analyse", {}).get("type_image", "?"),
            "decision_initiale": rapport.get("decision_initiale", {}).get("format", "?"),
            "decision_finale"  : rapport.get("decision_finale", {}).get("format", "?"),
            "decision_changee" : rapport.get("decision_changee_par_comparateur", False),
            "source_decision"  : rapport.get("decision_finale", {}).get("source", "?"),
            "ssim"             : rapport.get("metriques", {}).get("ssim", "?"),
            "psnr_db"          : rapport.get("metriques", {}).get("psnr_db", "?"),
            "mse"              : rapport.get("metriques", {}).get("mse", "?"),
            "tau"              : rapport.get("metriques", {}).get("taux_compression_pct", "?"),
            "statut"           : "✅" if "erreur" not in rapport else "❌"
        })
        time.sleep(0.3)

    duree = round(time.time() - debut, 1)
    resume_data = {
        "total"    : len(images),
        "succes"   : nb_succes,
        "erreurs"  : nb_erreurs,
        "duree_sec": duree,
        "resultats": resultats
    }
    resume_path = os.path.join(RAPPORTS_DIR, "resume_global.json")
    with open(resume_path, 'w', encoding='utf-8') as f:
        json.dump(resume_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*55}")
    print(f"  ✅ {nb_succes}/{len(images)} réussis en {duree}s")
    print(f"  📊 Résumé → {resume_path}")
    print(f"{'='*55}")

# ============================================================
# LANCEMENT
# ============================================================
if __name__ == '__main__':
    print("=" * 55)
    print("  Webhook Test Images - Port 5001")
    print("  n8n doit appeler :")
    print("  POST http://127.0.0.1:5001/lancer-tests")
    print("  GET  http://127.0.0.1:5001/resultats")
    print("=" * 55)
    webhook_app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False)