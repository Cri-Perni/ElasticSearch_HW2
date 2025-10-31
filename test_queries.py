import requests

URL = "http://localhost:5000/search"

queries = [
    # 2 single match title
    "title:file1", #-> file1.txt
    "title:cloud_computing", #->cloud_computing.txt
    # 1 double match on title
    "title:int", #-> intelligenza_artificiale.txt, internet_delle_cose.txt
    # 1 single match content
    'content:blockchain',#-> blockchain_e_criptovalute.txt
    # 3 multi match
    "content: quantistico intelligenza mappe", #-> ritorna 3 ->file
    # single match with AND
    'content: "IA" "mappe"', #-> ritorna 1 ->file
    # double match with OR
    'content: IA mappe', #-> ritorna 2 file
    
    "content:digitali Ai", #->ritorna 4 file
]

for i, q in enumerate(queries, 1):
    print(f"\n--- Query {i}: '{q}' ---")
    resp = requests.post(URL, data={"query": q})
    try:
        result = resp.json()
    except Exception:
        print("Risposta non valida:", resp.text)
        continue
    if resp.status_code == 200:
        print(f"Risultati trovati: {len(result)}")
        for hit in result[:5]:  # Mostra solo i primi 5 risultati
            print(f"- {hit['_source']['filename']}")
    else:
        print("Errore:", result.get("error", resp.text))