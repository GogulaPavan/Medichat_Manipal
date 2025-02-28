import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Attempt to import speech_recognition; if unavailable, disable voice input.
try:
    import speech_recognition as sr
    voice_supported = True
except Exception as e:
    voice_supported = False

# Configure Gemini API (Replace with your actual API key)
genai.configure(api_key="AIzaSyB_Sfa6qt63_Ap-Qjd86Tavmmg2iiSLgn4")

# Initialize the model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Function to scrape Manipal Hospital website
@st.cache_data
def scrape_manipal_info():
    url = "https://www.manipalhospitals.com/vijayawada/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()

# Store website content in cache for quick responses
if "manipal_data" not in st.session_state:
    st.session_state.manipal_data = scrape_manipal_info()

# Function to capture voice input with timeout and error handling, supporting multiple languages
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

# Voice input button with auto-send functionality (only if voice input is supported)
if voice_supported:
    if st.button("🎤 Use Voice Input"):
        voice_query = get_voice_input(language)
        if voice_query:
            st.success(f"🎙️ You said: {voice_query}")
            user_query = voice_query  # Update text field with recognized speech
            with st.spinner("Generating response..."):
                context = st.session_state.manipal_data
                prompt = f"{context}\n\nUser Query: {user_query}"
                try:
                    response = model.generate(prompt)
                    st.markdown(f"**🤖 Chatbot:** {response.text}", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error generating response: {e}")
        else:
            st.warning("No voice input detected.")
else:
    st.warning("Voice input is not supported in this deployment.")

# Send button for text input
if st.button("🚀 Send"):
    if user_query:
        with st.spinner("Generating response..."):
            context = st.session_state.manipal_data
            prompt = f"{context}\n\nUser Query: {user_query}"
            try:
                response = model.generate(prompt)
                st.markdown(f"**🤖 Chatbot:** {response.text}", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error generating response: {e}")
    else:
        st.warning("⚠️ Please enter a question or use the voice input feature.")

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini AI & Streamlit</div>', unsafe_allow_html=True)
