1. Introduzione

Questo progetto prende in input:
Un file Excel (.xlsx) con due colonne CodeX e CodeY (prima riga header).
Una cartella di immagini i cui nomi (senza estensione) corrispondono a uno dei due codici per riga.
Con un solo comando il tool:
Legge Excel e costruisce una mappa bidirezionale { CodeX→CodeY, CodeY→CodeX }.
Scansiona tutte le immagini in una cartella di input.
Per ciascuna immagine, trova il codice sorgente (CodeX o CodeY) e individua il codice “gemello” nella stessa riga.
Copia l’immagine in una cartella di output, rinominandola con il codice gemello + estensione originale.
Produce un log di successo e warning per file non abbinati o conflitti di nome.
2. Obiettivi

Semplicità: un single-command CLI.
Affidabilità: supporto estensioni comuni e gestione di nomi duplicati.
Portabilità: funziona su Windows, macOS, Linux.
Manutenibilità: modulare, facilmente estendibile in GUI o API.
3. Requisiti Funzionali

Input CLI
--excel PATH/TO/file.xlsx
--input-dir PATH/TO/images_in/
--output-dir PATH/TO/images_out/
Opzionali: --exts png,jpg,jpeg,bmp,gif e --dry-run
Mapping
Legge colonne header “CodeX” e “CodeY”
Crea dizionario { X: Y, Y: X }
Scansione e Ridenominazione
Processa ogni file il cui basename corrisponde a una chiave del dizionario
Copia in output-dir, rinominando con il valore associato + stessa estensione
Se il target esiste già, appende suffisso numerico _1, _2, …
Log
Stampa su console (o salva in export.log) tutte le operazioni, con warning per file skippati
4. Requisiti Non Funzionali

Lingua: Python 3.9+
Dipendenze leggere:
pandas
typer
pathlib, os, shutil
logging
Container: Docker basato su python:3.9-slim
Versioning: Git + GitHub
CI: GitHub Actions (test su Windows/macOS/Linux)
5. Architettura e Struttura

project_root/
├─ app.py               # Entrypoint CLI (Typer)
├─ renamer/
│   ├─ __init__.py
│   ├─ excel_map.py     # build_map(xlsx_path) → Dict[str,str]
│   └─ file_ops.py      # process_images(mapping, in_dir, out_dir, exts, dry_run)
├─ requirements.txt
├─ Dockerfile
└─ README.md
Descrizione componenti
app.py
Definisce i parametri Typer
Chiama excel_map.build_map() e file_ops.process_images()
excel_map.py
Usa pandas.read_excel()
Controlla header esatti “CodeX” e “CodeY”
Genera mappa bidirezionale
file_ops.py
Scansiona input_dir con pathlib.Path.iterdir()
Per ogni file controlla estensione e basename
Recupera codice target dalla mappa
Copia con shutil.copy2() in output_dir rinominando e gestendo conflitti
Logga con logging.info() e logging.warning()
6. Flusso Dati

Import Excel (.xlsx) → DataFrame con colonne CodeX, CodeY.
Costruzione Mappa → Dict[str,str]
Scan Cartella → lista di (basename, estensione, fullpath).
Match & Copy
Se basename in mappa → target = mappa[basename]
dest_filename = f"{target}{ext}", se esiste aggiungi _1, _2, …
shutil.copy2(src, output_dir / dest_filename)
Log Finale → numero file processati, skippati, errori.
7. Formati di Import/Export

Input Excel: .xlsx, header su prima riga esattamente “CodeX” e “CodeY”.
Input Immagini: qualsiasi estensione elencata in --exts.
Output Immagini: formato identico al file sorgente, conservata la qualità originale.
Log: plain-text su console; opzione di redirezionare in file export.log.
8. Esempio CLI

python app.py \
  --excel ./products.xlsx \
  --input-dir ./imgs_in/ \
  --output-dir ./imgs_out/ \
  --exts png,jpg,jpeg \
  --dry-run
9. Milestones

M1: Setup repo + virtualenv + requirements.txt
M2: excel_map.build_map() con test su Excel di esempio
M3: file_ops.process_images() base, copia semplice
M4: Gestione conflitti di nome e --dry-run
M5: Dockerfile + GitHub Actions per test multi-OS
M6: Documentazione README e esempi di run