#!/usr/bin/env python3
"""
Web App per Image Renamer - Interfaccia web semplice e funzionale.
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import logging

# Import dei nostri moduli
from renamer.csv_map import build_map_auto
from renamer.file_ops import process_images

# Configurazione Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Crea cartelle se non esistono
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configurazione logging per produzione
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.route('/')
def index():
    """Pagina principale dell'interfaccia."""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Pagina di test semplice per debug."""
    return send_file('test_simple.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Gestisce l'upload dei file e il processamento."""
    try:
        # Verifica che tutti i file necessari siano presenti
        if 'mapping_file' not in request.files or 'images' not in request.files:
            logging.error("File mancanti nella richiesta")
            return jsonify({'error': 'File mancanti. Servono mapping file e immagini.'}), 400
        
        mapping_file = request.files['mapping_file']
        images_files = request.files.getlist('images')
        
        logging.info(f"File mapping ricevuto: {mapping_file.filename}")
        logging.info(f"Numero immagini ricevute: {len(images_files)}")
        
        if not mapping_file.filename or not images_files:
            logging.error("Nessun file selezionato")
            return jsonify({'error': 'Nessun file selezionato.'}), 400
        
        # Crea cartelle temporanee
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, 'input')
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva il file di mapping
        mapping_path = os.path.join(temp_dir, mapping_file.filename)
        mapping_file.save(mapping_path)
        logging.info(f"File mapping salvato in: {mapping_path}")
        
        # Salva le immagini
        saved_images = []
        for img_file in images_files:
            if img_file.filename:
                img_path = os.path.join(input_dir, img_file.filename)
                img_file.save(img_path)
                saved_images.append(img_file.filename)
        
        logging.info(f"Immagini salvate: {len(saved_images)}")
        
        if not saved_images:
            return jsonify({'error': 'Nessuna immagine valida caricata.'}), 400
        
        # Costruisci la mappa dal file
        try:
            logging.info(f"Tentativo di leggere file mapping: {mapping_path}")
            mapping = build_map_auto(mapping_path)
            logging.info(f"Mappa costruita con successo: {len(mapping)//2} coppie")
        except Exception as e:
            logging.error(f"Errore nel file di mapping: {str(e)}")
            # Proviamo a leggere il file per vedere cosa contiene
            try:
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logging.info(f"Contenuto del file CSV:\n{content[:500]}")
            except:
                pass
            return jsonify({'error': f'Errore nel file di mapping: {str(e)}'}), 400
        
        # Processa le immagini
        try:
            processed, skipped, errors = process_images(
                mapping=mapping,
                input_dir=input_dir,
                output_dir=output_dir,
                exts=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
                dry_run=False
            )
            logging.info(f"Processamento completato: {processed} processati, {skipped} saltati, {errors} errori")
        except Exception as e:
            logging.error(f"Errore durante il processamento: {str(e)}")
            return jsonify({'error': f'Errore durante il processamento: {str(e)}'}), 500
        
        # Crea ZIP con i risultati
        zip_path = os.path.join(temp_dir, 'immagini_rinominate.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in Path(output_dir).iterdir():
                if file_path.is_file():
                    zipf.write(file_path, file_path.name)
        
        # Copia il ZIP nella cartella output per il download
        final_zip_path = os.path.join(app.config['OUTPUT_FOLDER'], 'immagini_rinominate.zip')
        shutil.copy2(zip_path, final_zip_path)
        
        # Pulisci file temporanei
        shutil.rmtree(temp_dir)
        
        return jsonify({
            'success': True,
            'message': 'Processamento completato con successo!',
            'stats': {
                'processed': processed,
                'skipped': skipped,
                'errors': errors,
                'total_uploaded': len(saved_images)
            },
            'download_url': '/download'
        })
        
    except Exception as e:
        logging.error(f"Errore nell'upload: {str(e)}")
        return jsonify({'error': f'Errore interno: {str(e)}'}), 500

@app.route('/download')
def download_result():
    """Permette di scaricare il file ZIP con i risultati."""
    zip_path = os.path.join(app.config['OUTPUT_FOLDER'], 'immagini_rinominate.zip')
    
    if not os.path.exists(zip_path):
        return jsonify({'error': 'File di download non trovato.'}), 404
    
    return send_file(
        zip_path,
        as_attachment=True,
        download_name='immagini_rinominate.zip',
        mimetype='application/zip'
    )

@app.route('/download-example-csv')
def download_example_csv():
    """Fornisce un file CSV di esempio corretto."""
    return send_file('test_mapping_correto.csv', as_attachment=True, download_name='esempio_mapping.csv')

@app.route('/health')
def health_check():
    """Health check per verificare che il server funzioni."""
    return jsonify({'status': 'ok', 'message': 'Server Image Renamer attivo!'})

if __name__ == '__main__':
    # Configurazione per produzione
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print("🚀 Avvio Image Renamer Web App...")
        print(f"📱 Apri il browser su: http://localhost:{port}")
    else:
        print(f"🌐 Image Renamer avviato in produzione sulla porta {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
