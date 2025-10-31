# Motore di Ricerca con Elasticsearch (HW2)

Applicazione Flask che indicizza file di testo in Elasticsearch e consente ricerche full‑text tramite diverse tipologie di query. Il focus è su Elasticsearch (mapping, analyzer, query). L’interfaccia web è minimale e serve per interagire con l’API.

## Funzionalità principali

- Indicizzazione automatica dei file `.txt` in `/data` all’avvio
- Re‑indicizzazione manuale tramite endpoint `/reindex`
- Ricerca per:
  - nome file (wildcard) — campo non analizzato (`keyword`)
  - contenuto con operatore OR/AND — `query_string`
  - frase esatta — `match_phrase`
  - multi‑campo (`filename` e `content`) — `multi_match`
- Risposte in JSON pronte per l’interfaccia web

## Architettura in breve

- Backend: Python + Flask (`app.py`)
- Motore di ricerca: Elasticsearch (8.x)
- Indexer: `FileIndexer` (`file_indexer.py`)
- Ricerca: `Searcher` (`searcher.py`)

### Mapping indice

```json
{
  "mappings": {
    "properties": {
      "filename": { "type": "keyword" },
      "content":  { "type": "text" }
    }
  }
}
```

- `filename` come `keyword`: non analizzato, utile per wildcard e confronti esatti
- `content` come `text`: usa lo standard analyzer di default (case‑insensitive, tokenizzazione generale)

## Requisiti

- Python 3.9+
- Elasticsearch in esecuzione su `http://localhost:9200`
- Pacchetti Python:
  - `Flask`
  - `elasticsearch` (client Python 8.x)
  - `requests` (per lo script di test)

Suggerimento (installazione rapida):
```powershell
pip install Flask elasticsearch requests
```

## Avvio

1) Avvia Elasticsearch (deve rispondere su `http://localhost:9200`).
2) Avvia l’app Flask:
```powershell
python .\app.py
```
All’avvio:
- verifica la connessione a Elasticsearch
- crea l’indice se non esiste
- indicizza i file in `/data`
- stampa a log il tempo di indicizzazione

Applicazione in ascolto su `http://localhost:5000`.

## Endpoint principali

- `POST /search`
  - Parametri (form): `query` (stringa)
  - Esempi di query supportate:
    - `title:file1` (wildcard su `filename` con `*` implicito ai lati)
    - `content:blockchain` (termine nel contenuto)
    - `content: IA mappe` (OR implicito via `query_string`)
    - `content: "IA" "mappe"` (AND — entrambe le frasi presenti)
    - `cloud` (multi_match su `filename` e `content`)

- `POST /reindex`
  - Forza la re‑indicizzazione dei file nella cartella `data`
  - Risponde con statistiche: nuovi/aggiornati/skippati/errori

## Esempi rapidi (PowerShell)

```powershell
# Ricerca per titolo
curl -X POST http://localhost:5000/search -d "query=title:file1"

# Ricerca OR nel contenuto
curl -X POST http://localhost:5000/search -d "query=content: IA mappe"

# Ricerca con vincolo di frasi (AND)
curl -X POST http://localhost:5000/search -d "query=content: \"IA\" \"mappe\""

# Re‑indicizzazione
curl -X POST http://localhost:5000/reindex
```

## Script di test

- `test_queries.py` invia una serie di query predefinite a `http://localhost:5000/search` e stampa i risultati.
- Esecuzione (con app già avviata):
```powershell
python .\test_queries.py
```
- Risultati di riferimento: `test_result.txt`

## Troubleshooting

- Errore avvio app: "Impossibile connettersi a Elasticsearch"
  - Verifica che Elasticsearch sia in esecuzione su `localhost:9200`
  - Controlla eventuali credenziali/SSL; il client è configurato con header di compatibilità 8.x
- Nessun risultato dalle query
  - Controlla che l’indice esista e che l’indicizzazione sia stata eseguita (`/reindex`)
  - Verifica i contenuti dei file in `data`

