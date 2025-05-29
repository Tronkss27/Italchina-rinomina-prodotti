"""
Modulo per operazioni sui file immagine.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple


def process_images(mapping: Dict[str, str], input_dir: str, output_dir: str, 
                  exts: List[str], dry_run: bool = False) -> Tuple[int, int, int]:
    """
    Processa le immagini rinominandole secondo la mappa fornita.
    
    Args:
        mapping: Dizionario di mapping {codice_sorgente: codice_target}
        input_dir: Cartella contenente le immagini di input
        output_dir: Cartella di destinazione per le immagini rinominate
        exts: Lista di estensioni permesse (es. ['png', 'jpg', 'jpeg'])
        dry_run: Se True, simula le operazioni senza eseguirle
        
    Returns:
        Tupla (processed, skipped, errors) con i conteggi delle operazioni
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Verifica che la cartella di input esista
    if not input_path.exists():
        raise FileNotFoundError(f"Cartella di input non trovata: {input_dir}")
    
    # Crea cartella di output se non esiste
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Normalizza estensioni (rimuovi punto e converti in lowercase)
    normalized_exts = [ext.lower().lstrip('.') for ext in exts]
    
    processed = 0
    skipped = 0
    errors = 0
    
    # Scansiona tutti i file nella cartella di input
    for file_path in input_path.iterdir():
        if not file_path.is_file():
            continue
            
        # Verifica estensione
        file_ext = file_path.suffix.lower().lstrip('.')
        if file_ext not in normalized_exts:
            logging.debug(f"File saltato (estensione non supportata): {file_path.name}")
            continue
        
        # Estrai basename (nome senza estensione)
        basename = file_path.stem
        
        # Cerca corrispondenza nella mappa
        if basename not in mapping:
            logging.warning(f"Codice non trovato nella mappa: {basename}")
            skipped += 1
            continue
        
        try:
            # Trova codice target
            target_code = mapping[basename]
            
            # Costruisci nome file di destinazione
            dest_filename = f"{target_code}{file_path.suffix}"
            dest_path = output_path / dest_filename
            
            # Gestisci conflitti di nome
            if dest_path.exists() and not dry_run:
                dest_path = _resolve_name_conflict(dest_path)
            
            # Esegui copia (se non in modalità dry-run)
            if dry_run:
                logging.info(f"[DRY-RUN] {file_path.name} -> {dest_path.name}")
            else:
                shutil.copy2(file_path, dest_path)
                logging.info(f"Rinominato: {file_path.name} -> {dest_path.name}")
            
            processed += 1
            
        except Exception as e:
            logging.error(f"Errore durante il processamento di {file_path.name}: {str(e)}")
            errors += 1
    
    # Log finale
    total_files = processed + skipped + errors
    logging.info(f"Operazioni completate:")
    logging.info(f"  - File processati: {processed}")
    logging.info(f"  - File saltati: {skipped}")
    logging.info(f"  - Errori: {errors}")
    logging.info(f"  - Totale file esaminati: {total_files}")
    
    return processed, skipped, errors


def _resolve_name_conflict(dest_path: Path) -> Path:
    """
    Risolve conflitti di nome aggiungendo suffissi numerici.
    
    Args:
        dest_path: Percorso di destinazione originale
        
    Returns:
        Nuovo percorso senza conflitti
    """
    counter = 1
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    
    while dest_path.exists():
        new_name = f"{stem}_{counter}{suffix}"
        dest_path = parent / new_name
        counter += 1
        
        # Limite di sicurezza per evitare loop infiniti
        if counter > 1000:
            raise RuntimeError(f"Troppi conflitti di nome per: {stem}{suffix}")
    
    return dest_path 