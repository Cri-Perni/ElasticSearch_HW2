from elasticsearch import Elasticsearch
import os

class FileIndexer:
    def __init__(self, es_client, index_name='file_search_index'):
        self.es = es_client
        self.index_name = index_name
    
    def create_index_if_not_exists(self):
        """Crea l'indice se non esiste"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                self.es.indices.create(
                    index=self.index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "filename": {"type": "keyword"},
                                "content": {"type": "text"}
                            }
                        }
                    }
                )
                print(f"Index '{self.index_name}' creato.")
            else:
                print(f"Index '{self.index_name}' gia' esistente.")
        except Exception as e:
            print(f"Errore nella creazione dell'indice: {e}")
            # Aggiungi questo metodo a FileIndexer
    def reset_index(self):
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
        print(f"Indice '{self.index_name}' eliminato.")
        self.create_index_if_not_exists()
    
    def index_file(self, filename, content):
        """Indicizza un singolo file"""
        doc = {
            'filename': filename,
            'content': content
        }
        
        # Controlla se il file è già indicizzato
        search_query = {
            "query": {
                "term": {
                    "filename": filename
                }
            }
        }
        response = self.es.search(index=self.index_name, body=search_query)
        
        if response['hits']['total']['value'] > 0:
            # File già esistente, controlla se il contenuto è cambiato
            doc_id = response['hits']['hits'][0]['_id']
            old_content = response['hits']['hits'][0]['_source']['content']
            
            if old_content != content:
                # Aggiorna il documento
                self.es.update(index=self.index_name, id=doc_id, body={"doc": doc})
                return 'updated'
            else:
                return 'skipped'
        else:
            # Nuovo file, indicizza
            self.es.index(index=self.index_name, document=doc)
            return 'indexed'
    
    def index_directory(self, directory='data'):
        """Indicizza tutti i file .txt in una directory"""
        if not os.path.exists(directory):
            print(f"Directory '{directory}' non trovata.")
            return {'error': f"Directory '{directory}' non trovata"}
        
        stats = {
            'new_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'errors': 0
        }
        
        print(f"\n--- Controllo nuovi file da indicizzare in '{directory}' ---")
        
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    result = self.index_file(filename, content)
                    
                    if result == 'indexed':
                        stats['new_files'] += 1
                        print(f"[OK] Indicizzato: {filename}")
                    elif result == 'updated':
                        stats['updated_files'] += 1
                        print(f"[OK] Aggiornato: {filename}")
                    else:
                        stats['skipped_files'] += 1
                        
                except Exception as e:
                    stats['errors'] += 1
                    print(f"[ERRORE] con {filename}: {e}")
        
        
        print(f"\n--- Riepilogo indicizzazione ---")
        print(f"Nuovi file: {stats['new_files']}")
        print(f"File aggiornati: {stats['updated_files']}")
        print(f"File gia' presenti: {stats['skipped_files']}")
        print(f"Errori: {stats['errors']}")
        print(f"Totale processati: {stats['new_files'] + stats['updated_files'] + stats['skipped_files']}\n")
        
        return stats