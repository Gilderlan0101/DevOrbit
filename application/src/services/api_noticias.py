from application.src.services.api_service import dataRequests, fetch_api_data

import requests
import logging
import httpx
from dotenv import load_dotenv
import os
load_dotenv()



def get_exact_count():
    """"
     Percorre a lista de posts retornada pela função `fetch_api_data()` e calcula a quantidade total de posts.

    Para cada post encontrado, incrementa o contador, que será utilizado para associar notícias 
    ou conteúdos específicos na página inicial.

    Returns:
        int: O número total de posts encontrados na lista retornada por `fetch_api_data()`.
    """
    
    post_count =0
    var = fetch_api_data() 

    if var is None:
        return 0
    
    
    
    for key in var: 
        
            post_count += 1  # Incrementar o contador se necessário
            continue

    return post_count

   



def get_top_stories(num_noticias=get_exact_count()):  # Define dinamicamente a quantidade de notícia

    api_url = os.getenv("API_NOTICIA") #  API 
    
    if not api_url:
        print("⚠️ Por favor, configure a chave da API de notícias! Acesse https://developer.nytimes.com/ para obter sua chave.")
        return []

    response = requests.get(api_url)

    if response.status_code == 200:
        news_data = response.json()
        
        # Pega os resultados da API
        if "results" in news_data:
            articles = news_data["results"][:num_noticias]  # Limita o número de notícias conforme num_noticias
            content = []
            
            for article in articles:
                title = article["title"]
                url = article["url"]
                summary = article.get("abstract", "Sem resumo disponível.")

                # Tenta pegar a imagem
                image_url = None
                if "multimedia" in article and article["multimedia"] is not None:
                    for multimedia in article["multimedia"]:
                        if multimedia.get("format") == 'Super Jumbo':  # Usando .get() para evitar KeyError
                            image_url = multimedia["url"]
                            break
                
                content.append({
                    "titulo": title,
                    "url": url,
                    "resumo": summary,
                    "imagem": image_url
                })
            
            return content  # Retorna a lista de notícias

        else:
            logging.error("Error: No results found in the Notices API response.")
            return []
    else:
        logging.error(f"Error: in api of noctic status code. {response.status_code}")
        return []

    
    
