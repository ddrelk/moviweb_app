import os
from dotenv import load_dotenv
import requests

load_dotenv()

RAPID_API_KEY = os.getenv('RAPID_API_KEY')

url = "https://chatgpt-api8.p.rapidapi.com/"


def chat_interface(question):
    payload = [
        {
            "content": question,
            "role": "user"
        }
    ]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "chatgpt-api8.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    json_response = response.json()
    if 'text' in json_response:
        result = json_response['text']
    else:
        result = json_response['choices'][0]['message']['content']
    return result


def ai_welcome(username):
    query = f""" Hey!

    You are now a movie app owner.

    The user {username}, just signed up for your website, Moviepedia, where he can add all his favorite 
    movies to his personal list and even leave reviews!Please welcome this new user stating the functions
    of the website.

    Please start your answer with a headline that greets the user! 
    """
    return query


def ai_prompt(username, movies_list):
    query = f""" Hey! My name is {username}. 

    You are now a movie expert, 
    and I need you to take a look at my list of favorite 
    movies and recommend me 1 to 3 movies to watch this weekend, that are not in my list.

    These are some movies I like {movies_list}, whatever you recommend me, 
    please include a small synopsis of the movie so I know what is it about.  

    Please start your answer with a headline that greets me and addresses to my name!
    """
    return query


def random_prompt(username):
    query = f"""My name is {username}. 
    You are now a movie expert. 
    Recommend a movie for me randomly and write brief summary about the movie.
    Please start your answer with a headline that greets me and addresses to my name!
    """
    return query


query = """You are now a movie app owner.

    The user Maude, just signed up for your website, Moviepedia, where he can add all his favorite 
    movies to his personal list and even leave reviews!Please welcome this new user.

    Please start your answer with a headline that greets the user!

    
    """

