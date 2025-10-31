from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import traceback
from file_indexer import FileIndexer
from searcher import Searcher
import re
import time
app = Flask(__name__)
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
    headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}
)
INDEX_NAME = 'file_search_index'

# Inizializza l'indexer
indexer = FileIndexer(es, INDEX_NAME)
searcher = Searcher(es, INDEX_NAME) 

@app.route('/')
def index():
    print("Index page requested")
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    print(f"Search endpoint called! Method: {request.method}")
    try:
        query = request.form.get('query', '') or request.args.get('query', '')
        print(f"Query received: '{query}'")
        if not query:
            return jsonify({"error": "Query vuota"}), 400

        if not es.indices.exists(index=INDEX_NAME):
            print(f"ERRORE: L'indice '{INDEX_NAME}' non esiste!")
            return jsonify({"error": f"Indice '{INDEX_NAME}' non trovato."}), 500

        # Usa la classe Searcher per gestire le query
        if query.startswith('title:'):
            filename_search = query.split('title:')[1].strip()
            response = searcher.search_by_title(filename_search)
        elif query.startswith('content:'):
            search_term = query.split('content:')[1].strip()
            phrases = re.findall(r'"([^"]+)"', search_term)
            if len(phrases) > 1:
                and_query = " AND ".join([f'"{p}"' for p in phrases])
                response = searcher.search_by_content(and_query)
            elif len(phrases) == 1:
                response = searcher.search_by_content_phrase(phrases[0])
            else:
                response = searcher.search_by_content(" OR ".join(search_term.split()))
        else:
            response = searcher.search_multi(query)

        print(f"Risultati trovati: {response['hits']['total']}")
        return jsonify(response['hits']['hits'])

    except Exception as e:
        print(f"ERRORE DETTAGLIATO:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/reindex', methods=['POST'])
def reindex():
    """Endpoint per forzare la re-indicizzazione manuale"""
    try:
        stats = indexer.index_directory()
        return jsonify({"message": "Re-indicizzazione completata", "stats": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Verifica connessione a Elasticsearch
    try:
        info = es.info()
        print(f"[OK] Connesso a Elasticsearch versione: {info['version']['number']}")
    except Exception as e:
        print(f"[ERRORE] Impossibile connettersi a Elasticsearch: {e}")
        exit(1)
    
    # Crea l'indice se non esiste
    indexer.create_index_if_not_exists()
    
    # Indicizza automaticamente i file all'avvio
    start = time.time()
    indexer.index_directory()
    end = time.time()
    print(f"[INFO] Indicizzazione completata in {end - start:.2f} secondi.")
    
    # Avvia Flask
    print("\n[OK] Avvio Flask...\n")
    app.run(debug=True)