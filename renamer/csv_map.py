"""
Modulo per costruire mapping bidirezionale da file CSV.
"""

import pandas as pd
from typing import Dict
import logging


def build_map_from_csv(csv_path: str) -> Dict[str, str]:
    """
    Legge un file CSV e costruisce una mappa bidirezionale tra colonna A e B.
    
    Args:
        csv_path: Percorso al file CSV
        
    Returns:
        Dizionario bidirezionale {ColonnaA: ColonnaB, ColonnaB: ColonnaA}
        
    Raises:
        FileNotFoundError: Se il file CSV non esiste
        ValueError: Se il file non ha almeno 2 colonne
    """
    try:
        # Prova diversi separatori e codifiche
        separators = [',', ';', '\t']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        df = None
        used_sep = None
        used_encoding = None
        
        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(csv_path, sep=sep, encoding=encoding)
                    if len(df.columns) >= 2:
                        used_sep = sep
                        used_encoding = encoding
                        break
                except:
                    continue
            if df is not None and len(df.columns) >= 2:
                break
        
        if df is None:
            raise ValueError("Impossibile leggere il file CSV con separatori comuni (virgola, punto e virgola, tab)")
        
        logging.info(f"CSV letto con separatore '{used_sep}' e codifica '{used_encoding}'")
        logging.info(f"Colonne trovate: {list(df.columns)}")
        
        # Verifica che ci siano almeno 2 colonne
        if len(df.columns) < 2:
            # Proviamo a leggere il file per vedere il contenuto
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    sample_lines = f.readlines()[:5]
                    sample_content = ''.join(sample_lines)
                    
                raise ValueError(f"""Il file CSV deve avere almeno 2 colonne separate da virgola.
Trovate: {len(df.columns)} colonna/e.

Contenuto attuale del file:
{sample_content}

Formato corretto richiesto:
NomeOriginale,NuovoNome
IMG001,PRD001
IMG002,PRD002

SUGGERIMENTI:
1. Assicurati che ci siano 2 colonne separate da virgola
2. La prima riga deve contenere gli header
3. Nessuna riga vuota all'inizio del file""")
            except:
                raise ValueError(f"Il file CSV deve avere almeno 2 colonne. Trovate: {len(df.columns)}")
        
        # Usa le prime due colonne
        col_a = df.columns[0]
        col_b = df.columns[1]
        
        logging.info(f"Usando colonne: '{col_a}' e '{col_b}'")
        
        # Rimuovi righe con valori NaN
        df_clean = df.dropna(subset=[col_a, col_b])
        
        if len(df_clean) == 0:
            raise ValueError("Nessuna riga valida trovata nel file CSV")
        
        # Costruisci mappa bidirezionale
        mapping = {}
        duplicates = []
        
        for _, row in df_clean.iterrows():
            code_a = str(row[col_a]).strip()
            code_b = str(row[col_b]).strip()
            
            # Verifica duplicati
            if code_a in mapping or code_b in mapping:
                duplicates.append(f"{code_a} <-> {code_b}")
                continue
                
            # Aggiungi mapping bidirezionale
            mapping[code_a] = code_b
            mapping[code_b] = code_a
        
        if duplicates:
            logging.warning(f"Righe duplicate ignorate: {duplicates}")
        
        logging.info(f"Mappa costruita con successo: {len(mapping)//2} coppie di codici")
        return mapping
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File CSV non trovato: {csv_path}")
    except Exception as e:
        if "almeno 2 colonne" in str(e):
            raise e  # Rilancia il nostro errore dettagliato
        raise ValueError(f"Errore durante la lettura del file CSV: {str(e)}")


def build_map_auto(file_path: str) -> Dict[str, str]:
    """
    Costruisce mappa automaticamente rilevando il formato (CSV o Excel).
    
    Args:
        file_path: Percorso al file
        
    Returns:
        Dizionario bidirezionale
    """
    file_extension = file_path.lower().split('.')[-1]
    
    if file_extension == 'csv':
        return build_map_from_csv(file_path)
    elif file_extension in ['xlsx', 'xls']:
        # Importa la funzione Excel esistente
        from .excel_map import build_map
        return build_map(file_path)
    else:
        raise ValueError(f"Formato file non supportato: {file_extension}. Usa CSV o Excel (.xlsx/.xls)") 