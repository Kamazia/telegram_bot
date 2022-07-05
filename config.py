import os


TOKEN = os.environ.get("TOKEN")
TOKEN_NEWS = os.environ.get("TOKEN_NEWS")
URL_NEWS ='https://free-news.p.rapidapi.com/v1/search'

# Headers

headers_news = {
            "X-RapidAPI-Host": "free-news.p.rapidapi.com",
            "X-RapidAPI-Key": TOKEN_NEWS
}