import time
import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch the movie poster using the movie ID
def fetch_poster(movie_id):
    max_retries = 3  # Number of retries in case of connection errors
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=d76159193bc8fb58406d48db264bd9f4')
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', 'placeholder.jpg')  # Return a placeholder path if not found
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)  # Wait for 1 second before retrying
    return "https://via.placeholder.com/500"  # Return a placeholder image URL if all retries fail

# Load the saved dataframe and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Define the recommend function to include fetching posters and URLs
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_urls = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_urls.append(f"https://www.themoviedb.org/movie/{movie_id}")
    return recommended_movies, recommended_movies_posters, recommended_movies_urls

# Streamlit app title and headers
st.set_page_config(page_title="Movie Recommender", layout="wide", page_icon="🎬")
st.title('Movie Recommender System')
st.markdown("Welcome to the Movie Recommender System! Choose a movie and get recommendations automatically.")

# Sidebar for options
st.sidebar.header("Settings")
selected_movie_name = st.sidebar.selectbox(
    "Select a Movie:",
    movies['title'].values
)

# Add custom CSS for styling
st.markdown("""
    <style>
    .stButton > button {
        background-color: #FF6347;
        color: white;
        border-radius: 12px;
        height: 3em;
        width: 12em;
        font-size: 16px;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #e55347;
    }
    .stSidebar > div > div > div > div {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
    }
    .footer {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
        border-top: 1px solid #ddd;
        padding-top: 10px;
    }
    .footer img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin-left: 10px;
    }
    .recommendation-card {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .recommendation-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Spinner while fetching recommendations
with st.spinner('Fetching movie recommendations...'):
    if selected_movie_name:
        names, posters, urls = recommend(selected_movie_name)

        # Displaying the results in a responsive layout
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"<div class='recommendation-card'>", unsafe_allow_html=True)
                st.markdown(f"<a href='{urls[i]}' target='_blank'><img src='{posters[i]}' alt='{names[i]}' style='width:100%; border-radius:10px;'></a>", unsafe_allow_html=True)
                st.markdown(f"<a href='{urls[i]}' target='_blank' class='movie-title'>{names[i]}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# Reset functionality - reset movie selection
if st.sidebar.button('Reset'):
    st.experimental_rerun()

# Footer section with your name and photo
st.markdown("---")
st.markdown("""
    <div class='footer'>
        <div style='text-align: center;'>
            <p>Made with ❤️ by Sonu. !</p>
        </div>
        <div>
            <img src='sonu.jpg' alt='Sonu'>
        </div>
    </div>
""", unsafe_allow_html=True)

# Extra features - add movie poster gallery for easier browsing
st.sidebar.subheader("Movie Poster Gallery")
for title, movie_id in zip(movies['title'].values[:10], movies['movie_id'].values[:10]):
    poster = fetch_poster(movie_id)
    st.sidebar.image(poster, caption=title, width=150)
