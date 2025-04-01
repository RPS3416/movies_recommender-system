# Import necessary libraries
import time
import streamlit as st
import pickle
import pandas as pd
import requests

# Define a function to fetch the movie poster using the movie ID
def fetch_poster(movie_id):
    max_retries = 3  # Number of retries in case of connection errors
    for attempt in range(max_retries):
        try:
            response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=d76159193bc8fb58406d48db264bd9f4')
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)  # Wait for 1 second before retrying
    return "https://via.placeholder.com/500"  # Return a placeholder image URL if all retries fail

# Load the saved dataframe and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Define the recommend function to include fetching posters
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Streamlit app title and headers
st.title('Movie Recommender System')


# Selectbox to choose a movie title
selected_movie_name = st.selectbox(
    "Select a movie",
    movies['title'].values)

# Recommend button functionality
#st.header('', divider="gray")

if st.button('Show Recommendation'):
    names,posters = recommend(selected_movie_name)
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



st.button("Reset", type="secondary")

# st.header('', divider="red")
# st.subheader('Vaishnavi Institute of Technology and Science Bhopal')
# st.header('', divider="gray")
