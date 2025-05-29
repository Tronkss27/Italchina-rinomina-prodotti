#!/usr/bin/env python3
"""
Image Renamer - MVP per rinominare immagini basato su mapping Excel.

Questo tool legge un file Excel con due colonne (CodeX, CodeY) e rinomina
le immagini in una cartella sostituendo i nomi con i codici "gemelli".
"""

import typer
import logging
import sys
from pathlib import Path
from typing import List

from renamer.excel_map import build_map
from renamer.file_ops import process_images

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

app = typer.Typer(
    name="image-renamer",
    help="Rinomina immagini basandosi su mapping Excel CodeX <-> CodeY",
    no_args_is_help=True
)


@app.command()
def main(
    excel: str = typer.Option(
        ...,
        "--excel",
        "-e",
        help="Percorso al file Excel (.xlsx) con colonne CodeX e CodeY"
    ),
    input_dir: str = typer.Option(
        ...,
        "--input-dir",
        "-i",
        help="Cartella contenente le immagini da rinominare"
    ),
    output_dir: str = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Cartella di destinazione per le immagini rinominate"
    ),
    exts: str = typer.Option(
        "png,jpg,jpeg,bmp,gif",
        "--exts",
        help="Estensioni file supportate (separate da virgola)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simula le operazioni senza eseguirle realmente"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Abilita output dettagliato (livello DEBUG)"
    )
):
    """
    Rinomina immagini basandosi su mapping Excel.
    
    Il tool legge un file Excel con colonne 'CodeX' e 'CodeY', costruisce
    una mappa bidirezionale e rinomina le immagini il cui nome (senza estensione)
    corrisponde a uno dei codici, sostituendolo con il codice "gemello".
    """
    
    # Configura livello di logging se verbose
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Modalità verbose abilitata")
    
    try:
        # Valida input
        excel_path = Path(excel)
        input_path = Path(input_dir)
        
        if not excel_path.exists():
            typer.echo(f"❌ Errore: File Excel non trovato: {excel}", err=True)
            raise typer.Exit(1)
        
        if not input_path.exists():
            typer.echo(f"❌ Errore: Cartella di input non trovata: {input_dir}", err=True)
            raise typer.Exit(1)
        
        if not input_path.is_dir():
            typer.echo(f"❌ Errore: Il percorso di input non è una cartella: {input_dir}", err=True)
            raise typer.Exit(1)
        
        # Prepara lista estensioni
        ext_list = [ext.strip() for ext in exts.split(',') if ext.strip()]
        
        if dry_run:
            typer.echo("🔍 Modalità DRY-RUN attivata - nessuna operazione verrà eseguita")
        
        typer.echo("📊 Costruzione mappa da file Excel...")
        
        # 1. Costruisci mappa da Excel
        mapping = build_map(str(excel_path))
        
        if not mapping:
            typer.echo("❌ Errore: Nessun mapping valido trovato nel file Excel", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"✅ Mappa costruita: {len(mapping)//2} coppie di codici")
        
        # 2. Processa immagini
        typer.echo("🖼️  Inizio processamento immagini...")
        
        processed, skipped, errors = process_images(
            mapping=mapping,
            input_dir=str(input_path),
            output_dir=output_dir,
            exts=ext_list,
            dry_run=dry_run
        )
        
        # 3. Report finale
        typer.echo("\n📋 REPORT FINALE:")
        typer.echo(f"  ✅ File processati: {processed}")
        typer.echo(f"  ⚠️  File saltati: {skipped}")
        typer.echo(f"  ❌ Errori: {errors}")
        
        if dry_run:
            typer.echo("\n💡 Esegui senza --dry-run per applicare le modifiche")
        elif processed > 0:
            typer.echo(f"\n🎉 Operazioni completate! File salvati in: {output_dir}")
        
        # Exit code basato sui risultati
        if errors > 0:
            raise typer.Exit(1)
        elif processed == 0:
            typer.echo("\n⚠️  Nessun file è stato processato")
            raise typer.Exit(1)
            
    except FileNotFoundError as e:
        typer.echo(f"❌ Errore: {str(e)}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"❌ Errore: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logging.error(f"Errore inaspettato: {str(e)}")
        typer.echo(f"❌ Errore inaspettato: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 