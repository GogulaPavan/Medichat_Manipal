import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import os

# Load API key securely from Streamlit Secrets or Environment Variable
api_key = st.secrets["GEMINI_API_KEY"] if "AIzaSyB_Sfa6qt63_Ap-Qjd86Tavmmg2iiSLgn4" in st.secrets else os.getenv("AIzaSyB_Sfa6qt63_Ap-Qjd86Tavmmg2iiSLgn4")
if not api_key:
    st.error("❌ API key is missing! Please set it in Streamlit Secrets or as an environment variable.")
    st.stop()

# Configure Gemini AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-pro")  # Use correct model name

# Function to scrape Manipal Hospital website (cached for performance)
@st.cache_data
def scrape_manipal_info():
    url = "https://www.manipalhospitals.com/vijayawada/"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()

# Store website content in cache for quick responses
if "manipal_data" not in st.session_state:
    st.session_state.manipal_data = scrape_manipal_info()

# Function to capture voice input with timeout and error handling
def get_voice_input(language="en-US"):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("🎙️ Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language=language)
            return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio. Please try again.")
    except sr.RequestError:
        st.error("❌ Speech recognition service is unavailable. Check your internet connection.")
    except Exception as e:
        st.error(f"❌ Voice input error: {e}")
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
st.title("🩺 MediChat Smart Hospital Chatbot")
st.write("Ask me anything about **Manipal Hospital Vijayawada**!")

# Language Selection for voice input
language = st.selectbox("Select voice recognition language", options=["en-US", "te-IN", "hi-IN"], index=0)

# User text input
user_query = st.text_input("💬 Your Question:")

# Voice input button with auto-send functionality
if st.button("🎤 Use Voice Input"):
    voice_query = get_voice_input(language)
    if voice_query:
        st.success(f"🎙️ You said: {voice_query}")
        user_query = voice_query  # Update text field with recognized speech

# Send button for text input (or recognized voice query)
if st.button("🚀 Send"):
    if user_query:
        with st.spinner("Generating response..."):
            context = st.session_state.manipal_data
            try:
                response = model.generate_content(f"{context}\n\nUser Query: {user_query}")
                st.markdown(f"**🤖 Chatbot:** {response.text}", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error generating response: {e}")
    else:
        st.warning("⚠️ Please enter a question or use the voice input feature.")

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini AI & Streamlit</div>', unsafe_allow_html=True)
