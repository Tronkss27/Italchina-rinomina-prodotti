"""
Modulo per costruire mapping bidirezionale da file Excel.
"""

import pandas as pd
from typing import Dict
import logging


def build_map(xlsx_path: str) -> Dict[str, str]:
    """
    Legge un file Excel e costruisce una mappa bidirezionale tra CodeX e CodeY.
    
    Args:
        xlsx_path: Percorso al file Excel (.xlsx)
        
    Returns:
        Dizionario bidirezionale {CodeX: CodeY, CodeY: CodeX}
        
    Raises:
        FileNotFoundError: Se il file Excel non esiste
        ValueError: Se le colonne richieste non sono presenti
    """
    try:
        # Leggi il file Excel
        df = pd.read_excel(xlsx_path)
        
        # Verifica che le colonne richieste esistano
        required_columns = ['CodeX', 'CodeY']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Colonne mancanti nel file Excel: {missing_columns}. "
                           f"Colonne presenti: {list(df.columns)}")
        
        # Rimuovi righe con valori NaN
        df_clean = df.dropna(subset=['CodeX', 'CodeY'])
        
        if len(df_clean) == 0:
            raise ValueError("Nessuna riga valida trovata nel file Excel")
        
        # Costruisci mappa bidirezionale
        mapping = {}
        duplicates = []
        
        for _, row in df_clean.iterrows():
            code_x = str(row['CodeX']).strip()
            code_y = str(row['CodeY']).strip()
            
            # Verifica duplicati
            if code_x in mapping or code_y in mapping:
                duplicates.append(f"{code_x} <-> {code_y}")
                continue
                
            # Aggiungi mapping bidirezionale
            mapping[code_x] = code_y
            mapping[code_y] = code_x
        
        if duplicates:
            logging.warning(f"Righe duplicate ignorate: {duplicates}")
        
        logging.info(f"Mappa costruita con successo: {len(mapping)//2} coppie di codici")
        return mapping
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File Excel non trovato: {xlsx_path}")
    except Exception as e:
        raise ValueError(f"Errore durante la lettura del file Excel: {str(e)}") 