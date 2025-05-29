# Image Renamer MVP

Un tool Python per rinominare automaticamente immagini basandosi su mapping Excel con codici bidirezionali.

## 🎯 Funzionalità

- **Mapping bidirezionale**: Legge file Excel con colonne `CodeX` e `CodeY`
- **Rinominazione automatica**: Sostituisce i nomi file con i codici "gemelli"
- **Gestione conflitti**: Aggiunge suffissi numerici per evitare sovrascritture
- **Modalità dry-run**: Simula le operazioni senza eseguirle
- **Logging dettagliato**: Report completo delle operazioni
- **Supporto multi-formato**: PNG, JPG, JPEG, BMP, GIF
- **Containerizzato**: Supporto Docker per portabilità

## 📋 Requisiti

- Python 3.9+
- pandas >= 1.5.0
- typer >= 0.9.0
- openpyxl >= 3.1.0

## 🚀 Installazione

### Metodo 1: Installazione locale

```bash
# Clona il repository
git clone <repository-url>
cd image-renamer

# Crea ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oppure
venv\Scripts\activate     # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### Metodo 2: Docker

```bash
# Build dell'immagine
docker build -t image-renamer .

# Verifica installazione
docker run --rm image-renamer --help
```

## 📖 Uso

### Sintassi base

```bash
python app.py --excel FILE.xlsx --input-dir CARTELLA_INPUT --output-dir CARTELLA_OUTPUT
```

### Parametri

| Parametro | Obbligatorio | Descrizione |
|-----------|--------------|-------------|
| `--excel`, `-e` | ✅ | Percorso al file Excel (.xlsx) con colonne CodeX e CodeY |
| `--input-dir`, `-i` | ✅ | Cartella contenente le immagini da rinominare |
| `--output-dir`, `-o` | ✅ | Cartella di destinazione per le immagini rinominate |
| `--exts` | ❌ | Estensioni supportate (default: png,jpg,jpeg,bmp,gif) |
| `--dry-run` | ❌ | Simula operazioni senza eseguirle |
| `--verbose`, `-v` | ❌ | Output dettagliato per debugging |

### Esempi

#### Esempio base
```bash
python app.py \
  --excel ./products.xlsx \
  --input-dir ./images_input/ \
  --output-dir ./images_output/
```

#### Con modalità dry-run
```bash
python app.py \
  --excel ./products.xlsx \
  --input-dir ./images_input/ \
  --output-dir ./images_output/ \
  --dry-run
```

#### Con estensioni personalizzate
```bash
python app.py \
  --excel ./products.xlsx \
  --input-dir ./images_input/ \
  --output-dir ./images_output/ \
  --exts png,jpg
```

#### Con Docker
```bash
# Prepara i volumi
mkdir -p ./data/input ./data/output
cp products.xlsx ./data/
cp *.jpg ./data/input/

# Esegui il container
docker run --rm \
  -v $(pwd)/data:/app/data \
  image-renamer \
  --excel /app/data/products.xlsx \
  --input-dir /app/data/input \
  --output-dir /app/data/output
```

## 📊 Formato File Excel

Il file Excel deve avere:
- **Prima riga**: Header con esattamente `CodeX` e `CodeY`
- **Righe successive**: Coppie di codici corrispondenti

### Esempio:

| CodeX | CodeY |
|-------|-------|
| IMG001 | PRD001 |
| IMG002 | PRD002 |
| SKU123 | ITEM456 |

## 🔄 Funzionamento

1. **Lettura Excel**: Costruisce mappa bidirezionale `{CodeX: CodeY, CodeY: CodeX}`
2. **Scansione immagini**: Trova file con estensioni supportate
3. **Matching**: Cerca nome file (senza estensione) nella mappa
4. **Rinominazione**: Copia file con nuovo nome nella cartella output
5. **Gestione conflitti**: Aggiunge suffissi `_1`, `_2`, etc. se necessario

### Esempio di trasformazione:
```
Input:  IMG001.jpg → Output: PRD001.jpg
Input:  PRD002.png → Output: IMG002.png
```

## 📝 Output e Logging

Il tool fornisce:
- **Progress real-time**: Durante l'esecuzione
- **Report finale**: Conteggio file processati, saltati, errori
- **Warning**: Per file non trovati nella mappa
- **Errori dettagliati**: Con stack trace se `--verbose`

### Esempio output:
```
📊 Costruzione mappa da file Excel...
✅ Mappa costruita: 150 coppie di codici
🖼️  Inizio processamento immagini...
2024-01-15 10:30:15 - INFO - Rinominato: IMG001.jpg -> PRD001.jpg
2024-01-15 10:30:15 - WARNING - Codice non trovato nella mappa: UNKNOWN123
2024-01-15 10:30:16 - INFO - Rinominato: SKU456.png -> ITEM789.png

📋 REPORT FINALE:
  ✅ File processati: 142
  ⚠️  File saltati: 8
  ❌ Errori: 0

🎉 Operazioni completate! File salvati in: ./images_output/
```

## 🗂️ Struttura Progetto

```
image-renamer/
├── app.py                 # Entry point CLI con Typer
├── renamer/
│   ├── __init__.py        # Package marker
│   ├── excel_map.py       # Gestione mapping Excel
│   └── file_ops.py        # Operazioni sui file
├── requirements.txt       # Dipendenze Python
├── Dockerfile            # Containerizzazione
├── README.md             # Documentazione
└── documentazione.md     # Specifica tecnica
```

## 🔧 Sviluppo

### Test locale
```bash
# Installa in modalità sviluppo
pip install -e .

# Esegui con dati di test
python app.py --excel test/sample.xlsx --input-dir test/images --output-dir test/output --dry-run
```

### Debug
```bash
# Abilita logging dettagliato
python app.py --verbose --excel file.xlsx --input-dir in/ --output-dir out/
```

## ⚠️ Limitazioni e Note

- **Dipendenze file**: I nomi file devono corrispondere esattamente ai codici Excel
- **Gestione memoria**: Per dataset molto grandi (>10K immagini), monitorare l'uso RAM
- **Concorrenza**: Non supporta elaborazione parallela (v1.0)
- **Backup**: Il tool non crea backup automatici dei file originali

## 🚨 Troubleshooting

### Errore "Colonne mancanti nel file Excel"
- Verifica che il file Excel abbia esattamente le colonne `CodeX` e `CodeY`
- Controlla che non ci siano spazi extra nei nomi delle colonne

### Nessun file processato
- Verifica che le estensioni dei file siano in `--exts`
- Controlla che i nomi file (senza estensione) esistano nella mappa Excel
- Usa `--verbose` per vedere file saltati

### Errori di permessi
- Verifica permessi di lettura sulla cartella input
- Verifica permessi di scrittura sulla cartella output
- Con Docker, controlla i mount dei volumi

## 📄 Licenza

Questo è un progetto MVP. Definire licenza in base alle necessità.

## 🤝 Contributi

Per bug report e feature request, aprire issue nel repository del progetto. 