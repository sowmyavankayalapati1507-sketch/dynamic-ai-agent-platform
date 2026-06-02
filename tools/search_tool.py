import requests

def search_web(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"

        response = requests.get(url)
        data = response.json()

        return {
            "query": query,
            "result": data.get("AbstractText", "No results found")
        }

    except Exception as e:
        return {
            "error": str(e)
        }