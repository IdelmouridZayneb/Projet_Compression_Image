import sys
import json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.ndimage import convolve
import os
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def rgb2gray(I):
    r, g, b = I[:,:,0], I[:,:,1], I[:,:,2]
    return 0.2989 * r + 0.5870 * g + 0.1140 * b

def variance(image):
    m = np.mean(image)
    l, c = image.shape
    return (1/(l*c)) * np.sum((image-m)**2)

def energy(image):
    return float(np.sum(image**2))

def entropy(image):
    hist, _ = np.histogram(image.flatten(), bins=256, range=(0, 256))
    probs = hist / image.size
    probs = probs[probs > 0]
    return round(float(-np.sum(probs * np.log2(probs))), 4)

def contrast(image):
    l, c = image.shape
    cont = 0
    for i in range(l):
        for j in range(c):
            cont += ((i-j)**2) * image[i][j]
    return cont

def homogenity(image):
    l, c = image.shape
    moment = 0
    for i in range(l):
        for j in range(c):
            moment += image[i][j] / (1 + np.abs(i-j))
    return moment

def avg_color(matrice):
    return float(np.mean(matrice))

def hist_rgb(image, bins=256):
    resultats = {}
    canaux = ['rouge', 'vert', 'bleu']
    for i, canal in enumerate(canaux):
        valeurs = image[:,:,i].flatten()
        resultats[canal] = {
            'moyenne':    round(float(np.mean(valeurs)), 2),
            'ecart_type': round(float(np.std(valeurs)), 2),
            'min':        int(np.min(valeurs)),
            'max':        int(np.max(valeurs))
        }
    return resultats

def extraire_metadonnees(chemin, image):
    largeur, hauteur = image.size
    taille_kb = os.path.getsize(chemin) / 1024
    ext = os.path.splitext(chemin)[1].lower()
    format_map = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}
    return {
        'nom_fichier':   os.path.basename(chemin),
        'largeur':       largeur,
        'hauteur':       hauteur,
        'format':        format_map.get(ext, str(image.format)),
        'extension':     ext,
        'mode':          image.mode,
        'taille_kb':     round(taille_kb, 2),
        'nombre_pixels': largeur * hauteur
    }

def detecter_contours(chemin_image):
    img = Image.open(chemin_image).convert('L')
    img_array = np.array(img, dtype=np.float64)
    sobel_x = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    sobel_y = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
    grad_x = convolve(img_array, sobel_x)
    grad_y = convolve(img_array, sobel_y)
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    laplacien = np.array([[0,1,0],[1,-4,1],[0,1,0]])
    lap = convolve(img_array, laplacien)
    return {
        'nombre_contours': int(np.sum(magnitude > 100)),
        'nettete':         round(float(np.var(lap)), 2)
    }

def analyser_morphologie(chemin_image):
    img = Image.open(chemin_image).convert('L')
    img_bin = (np.array(img) > 128).astype(np.uint8)
    elem_struct = np.array([[0,1,0],[0,1,1],[0,1,0]], dtype=np.uint8)
    dilatee = ndimage.binary_dilation(img_bin, structure=elem_struct).astype(np.uint8)
    erodee  = ndimage.binary_erosion(img_bin, structure=elem_struct).astype(np.uint8)
    contours_morpho = dilatee - erodee
    pixels_blancs   = int(np.sum(img_bin))
    pixels_contours = int(np.sum(contours_morpho))
    return {
        'pixels_contours_morpho': pixels_contours,
        'ratio_complexite':       round(pixels_contours / (pixels_blancs + 1), 4)
    }

def co_occurence_0(image, level=256):
    co = np.zeros((level, level))
    rows, cols = image.shape
    for i in range(rows):
        for j in range(cols - 1):
            row_val = int(image[i, j])
            col_val = int(image[i, j + 1])
            co[row_val, col_val] += 1
    if np.sum(co) != 0:
        co = co / np.sum(co)
    return co

def co_occurence_90(image, level=256):
    co = np.zeros((level, level), dtype=float)
    l, c = image.shape
    for i in range(1, l):
        for j in range(c):
            rows = int(image[i, j])
            cols = int(image[i-1, j])
            co[rows, cols] += 1
    if np.sum(co) != 0:
        co = co / np.sum(co)
    return co

def glcm_features(glcm):
    i_idx, j_idx = np.meshgrid(
        np.arange(glcm.shape[0]),
        np.arange(glcm.shape[1]),
        indexing='ij'
    )
    contrast_val    = float(np.sum(glcm * (i_idx - j_idx)**2))
    homogeneity_val = float(np.sum(glcm / (1 + np.abs(i_idx - j_idx))))
    energy_val      = float(np.sum(glcm**2))
    g = glcm[glcm > 0]
    entropy_val     = float(-np.sum(g * np.log2(g)))
    return {
        'contrast':    round(contrast_val, 4),
        'homogeneity': round(homogeneity_val, 4),
        'energy':      round(energy_val, 6),
        'entropy':     round(entropy_val, 4)
    }

def analyser_glcm(image_gray):
    img_small = np.clip(image_gray[:80, :80], 0, 255).astype(int)
    if np.std(img_small) < 1:
        return {
            'glcm_0deg':  {'contrast': 0, 'homogeneity': 1, 'energy': 1, 'entropy': 0},
            'glcm_90deg': {'contrast': 0, 'homogeneity': 1, 'energy': 1, 'entropy': 0},
            'note': 'image uniforme'
        }
    glcm_0  = co_occurence_0(img_small, level=256)
    glcm_90 = co_occurence_90(img_small, level=256)
    return {
        'glcm_0deg':  glcm_features(glcm_0),
        'glcm_90deg': glcm_features(glcm_90)
    }

def detecter_type_image(features, histogramme):
    entropy_val = features['entropy']
    couleur_moy = histogramme['couleur_moyenne']
    r, g, b = couleur_moy[0], couleur_moy[1], couleur_moy[2]
    diff_couleurs = abs(r-g) + abs(g-b) + abs(r-b)
    if entropy_val > 6.0 and diff_couleurs > 30:
        return 'photo'
    elif entropy_val < 3.0 and diff_couleurs < 20:
        return 'document'
    elif entropy_val < 4.0 and diff_couleurs > 20:
        return 'graphique'
    else:
        return 'screenshot'

def analyser_ocr(chemin_image):
    try:
        img = Image.open(chemin_image).convert('L')
        texte = pytesseract.image_to_string(img, lang='fra+eng')
        texte = texte.strip()
        mots = [m for m in texte.split() if len(m) > 1]
        return {
            'contient_texte': len(mots) > 5,
            'nombre_mots':    len(mots),
            'texte_extrait':  texte[:200] if texte else ''
        }
    except Exception as e:
        return {
            'contient_texte': False,
            'nombre_mots':    0,
            'texte_extrait':  f'Erreur OCR: {str(e)}'
        }

def agent_analyste(chemin_image):
    image     = Image.open(chemin_image)
    image_rgb = image.convert('RGB')
    img_array = np.array(image_rgb)
    img_gray  = rgb2gray(img_array)
    img_small = img_gray[:50, :50]
    metadonnees = extraire_metadonnees(chemin_image, image)
    features = {
        'variance':   round(float(variance(img_gray)), 4),
        'energy':     round(float(energy(img_gray)), 4),
        'entropy':    round(float(entropy(img_gray)), 4),
        'contrast':   round(float(contrast(img_small)), 4),
        'homogenity': round(float(homogenity(img_small)), 4)
    }
    histogramme = hist_rgb(img_array)
    histogramme['couleur_moyenne'] = [
        round(avg_color(img_array[:,:,0]), 2),
        round(avg_color(img_array[:,:,1]), 2),
        round(avg_color(img_array[:,:,2]), 2)
    ]
    contours    = detecter_contours(chemin_image)
    morphologie = analyser_morphologie(chemin_image)
    glcm        = analyser_glcm(img_gray)
    type_image  = detecter_type_image(features, histogramme)
    ocr         = analyser_ocr(chemin_image)
    resultat = {
        'image':                 chemin_image,
        'type_image':            type_image,
        'metadonnees':           metadonnees,
        'features_statistiques': features,
        'histogramme_rgb':       histogramme,
        'contours':              contours,
        'morphologie':           morphologie,
        'glcm':                  glcm,
        'ocr':                   ocr
    }
    print(json.dumps(resultat, ensure_ascii=False))
    return resultat

if __name__ == '__main__':
    chemin = sys.argv[1]
    agent_analyste(chemin)
