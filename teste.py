
from application.src.services.api_service import dataRequests

var = dataRequests()
print(var)

class SearchData:
    def __init__(
            self, username: str, title: str, resulm:str
            ):
        
        self.username = username
        self.title = title
        self.resulm = resulm

    
    def Search(self, query: str):
        data = self.PickingupDataForResearch()
        

        if query.lower() in data["title"].lower():
            return f"{query}: {data['title']} \n  {data['resulm']}"
        else:
            return f"Resultado não encontrado para {query}"



    def PickingupDataForResearch(self):
        return  {
            "username": self.username,
            "title": self.title,
            "resulm": self.resulm

        }


var = SearchData()

resultado1 = var.Search('como sabe o tamanho de um modolo')


print(resultado1)
