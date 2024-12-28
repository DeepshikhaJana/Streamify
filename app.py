import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

st.markdown("""
<style>

.movie-title {
    font-family: 'Montserrat', sans-serif;
}
    .block-container {
        max-width: 95% !important; 
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container {
        max-width: 95% !important;
        padding: 2rem;
    }
    
    .selectbox-label {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
    }
    
    </style>
""", unsafe_allow_html=True)


def fetch_poster(title):
    # Search for movie by title
    search_url = f'https://www.omdbapi.com/?t={title}&apikey=50c4beb9'
    print(f"Searching for movie: {title}") 

    response = requests.get(search_url)
    data = response.json()

    #error handling
    if data.get('Response') == 'True' and 'Poster' in data:
        print(f"Found poster for: {title}")
        return data['Poster']
    else:
        print(f"Failed to fetch poster for movie: {title}")
        print(f"API Response: {data}")
        return "https://via.placeholder.com/300x450?text=No+Poster+Available"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_movies_posters.append(fetch_poster(title))
    return recommended_movies, recommended_movies_posters


movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
movies_list = movies_list['title'].values

st.markdown("<h1 style='font-size: 4rem;'>STREAMIFY 🍿🎥</h1>", unsafe_allow_html=True)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.markdown("<p class='selectbox-label'>What do you want to watch?</p>", unsafe_allow_html=True)
option = st.selectbox(
    label=" ",  
    options=movies_list,
    key="movie_select"
)

if st.button("Recommend", type="primary"):
    names, posters = recommend(option)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])


load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
OMDB_BASE_URL = "http://www.omdbapi.com/"

def get_movie_details(query):
    params = {
        "apikey": OMDB_API_KEY,
        "t": query  
    }
    response = requests.get(OMDB_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return f"**Title:** {data['Title']}\n\n**Year:** {data['Year']}\n\n**Genre:** {data['Genre']}\n\n**Plot:** {data['Plot']}\n\n**IMDB Rating:** {data['imdbRating']}"
        else:
            return "Sorry, I couldn't find the movie you're looking for. Please try another title."
    else:
        return "Error fetching data. Please try again later."


st.title("Movie Explorer 🎬")
st.write("Discover details, trivia, and more about your favorite films!")

user_input = st.text_input("")

if user_input:
    response = get_movie_details(user_input)
    st.markdown(response)

def generate_content(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        
        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
        return generated_text  
    else:
        return {"error": f"Request failed with status code {response.status_code}"}


st.title("Movie Chatbot 🤖")
st.write("Ask the bot whatever you want to")

default_prompt = "I want to watch horror movies"
user_input = st.text_input("Type your prompt here:", value=default_prompt)

if st.button("Clear"):
    user_input = ""  

if user_input:
    result = generate_content(user_input)  
    if isinstance(result, dict) and "error" in result:
        st.error(result["error"]) 
    else:
        st.markdown(result)
