from application.src.services.api_service import dataRequests

class SearchData:
    def __init__(self):
        self.username = ""
        self.title = ""
        self.resulm = ""

    def Search(self, query: str):
        # Recupera todos os dados para pesquisa
        data = self.PickingupDataForResearch()

        # Filtra os resultados que correspondem ao termo pesquisado
        matching_results = [
            {
                "username": item["username"],
                "title": item["title"],
                "resulm": item["resulm"],
                "likes": item["likes"],
                "user_id": item["user_id"]
            }
            for item in data
            if query.lower() in item["title"].lower() or query.lower() in item["resulm"].lower()
        ]

        # Retorna os resultados como lista de dicionários
        return matching_results

    def PickingupDataForResearch(self):
        # Pega todos os dados da API
        data = dataRequests()
        result = []

        # Processa os dados retornados da API
        if data["todos_os_posts"]:
            for var in data["todos_os_posts"]:
                if isinstance(var, dict):
                    result.append(
                        {
                            "username": var.get("nome", "Desconhecido").capitalize(),
                            "title": var.get("titulo", "vazio").capitalize(),
                            "resulm": var.get("post", "")[:50] + '...', 
                            "ID": var.get("id", None),
                            "likes": int(var.get("likes", 0)),
                            "user_id": var.get("user_id")
                        }
                    )
        return result
