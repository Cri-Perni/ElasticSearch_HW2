class Searcher:
    def __init__(self, es_client, index_name):
        self.es = es_client
        self.index_name = index_name

    def search_by_title(self, title):
        return self.es.search(index=self.index_name, body={
            "query": {
                "wildcard": {
                    "filename": f"*{title}*"
                }
            }
        })

    def search_by_content(self, content):
        operator = "AND" if "AND" in content else "OR"
        content = content.replace("AND", "").replace("OR", "")
        return self.es.search(index=self.index_name, body={
            "query": {
                "query_string": {
                    "default_field": "content",
                    "query": content,
                    "default_operator": operator,
                    "analyze_wildcard": False
                }
            }
        })

    def search_multi(self, query):
        return self.es.search(index=self.index_name, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["filename", "content"]
                }
            }
        })
    
    def search_by_content_phrase(self, phrase):
        return self.es.search(index=self.index_name, body={
            "query": {
                "match_phrase": {
                    "content": phrase
                }
            }
        })