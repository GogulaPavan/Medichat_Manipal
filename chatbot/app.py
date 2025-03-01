import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr

# Configure Gemini API using Streamlit secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("\u274c Gemini API key not found. Please add it to Streamlit secrets.")
    st.stop()

# Initialize the model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Function to scrape Manipal Hospital website
@st.cache_data
def scrape_manipal_info():
    try:
        url = "https://www.manipalhospitals.com/vijayawada/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        st.error(f"\u274c Error fetching data from Manipal Hospital website: {e}")
        return ""

# Store website content in cache for quick responses
if "manipal_data" not in st.session_state:
    st.session_state.manipal_data = scrape_manipal_info()

# Function to capture voice input with timeout and error handling
def get_voice_input(language="en-US"):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("\ud83c\udfa7 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language=language)
            return text
    except sr.UnknownValueError:
        st.error("\u274c Could not understand the audio. Please try again.")
    except sr.RequestError:
        st.error("\u274c Speech recognition service is unavailable. Check your internet connection.")
    except Exception as e:
        st.error(f"\u274c Voice input error: {e}")
    return None

# Streamlit UI with enhanced styles
st.markdown(
    """
    <style>
    h1 { color: #4F8BF9; text-align: center; font-size: 2.5rem; }
    h2 { color: #2E86C1; font-size: 1.8rem; margin-bottom: 10px; }
    .stTextInput input { border: 2px solid #4F8BF9; border-radius: 5px; padding: 10px; font-size: 1rem; }
    .stButton button { background-color: #4F8BF9; color: white; border-radius: 5px; padding: 10px 20px; font-size: 1rem; border: none; transition: 0.3s; }
    .stButton button:hover { background-color: #2E86C1; }
    .stMarkdown { background-color: #F4F6F6; padding: 15px; border-radius: 5px; border: 1px solid #D0D3D4; margin-top: 20px; }
    .footer { text-align: center; margin-top: 40px; font-size: 0.9rem; color: #7F8C8D; }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title and Instructions
st.title("\ud83e\uddec MediChat Smart Hospital Chatbot")
st.write("Ask me anything about **Manipal Hospital Vijayawada**!")

# Language Selection for voice input
language = st.selectbox("Select voice recognition language", options=["en-US", "te-IN", "hi-IN"], index=0)

# User text input
user_query = st.text_input("\ud83d\udcac Your Question:")

# Voice input button with auto-send functionality
if st.button("\ud83c\udfa4 Use Voice Input"):
    voice_query = get_voice_input(language)
    if voice_query:
        st.success(f"\ud83c\udfa7 You said: {voice_query}")
        user_query = voice_query
        with st.spinner("Generating response..."):
            context = st.session_state.manipal_data
            response = model.generate_content(f"{context}\n\nUser Query: {user_query}")
            st.markdown(f"**\ud83e\udd16 Chatbot:** {response.text}", unsafe_allow_html=True)
    else:
        st.warning("No voice input detected.")

# Send button for text input (if not using voice input)
if st.button("\ud83d\ude80 Send"):
    if user_query:
        with st.spinner("Generating response..."):
            context = st.session_state.manipal_data
            response = model.generate_content(f"{context}\n\nUser Query: {user_query}")
            st.markdown(f"**\ud83e\udd16 Chatbot:** {response.text}", unsafe_allow_html=True)
    else:
        st.warning("\u26a0\ufe0f Please enter a question or use the voice input feature.")

# Footer
st.markdown('<div class="footer">\ud83d\ude80 Powered by Gemini AI & Streamlit</div>', unsafe_allow_html=True)
