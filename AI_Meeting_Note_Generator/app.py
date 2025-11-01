import streamlit as st
import openai
import tempfile
import os
from io import BytesIO

# ----------------------- App Configuration -----------------------
st.set_page_config(
    page_title="AI Meeting Note Generator",
    page_icon="",
    layout="centered"
)

# ----------------------- Custom Styling -----------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #F8F7F4, #E8E3D9);
    font-family: 'Inter', sans-serif;
}
.main-title {
    text-align: center;
    font-size: 2.2em;
    color: #2E1A47; /* Deep plum - luxurious tone */
    font-weight: 700;
    margin-bottom: 8px;
}
.subtitle {
    text-align: center;
    color: #4C3575; /* Royal purple accent */
    font-size: 1em;
    margin-bottom: 25px;
}
.stButton>button {
    background: linear-gradient(90deg, #2E1A47, #4C3575);
    color: #F8F7F4;
    border-radius: 10px;
    padding: 0.6em 1.5em;
    font-size: 1em;
    font-weight: 500;
    transition: 0.3s;
    border: none;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #4C3575, #6A4CA3);
}
footer {
    text-align: center;
    color: #5C5470;
    font-size: 0.9em;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------- API Key Verification -----------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("OpenAI API key not found. Please set it in your environment before using this application.")
    st.stop()

# ----------------------- Page Header -----------------------
st.markdown("<div class='main-title'>AI Meeting Note Generator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Convert meeting audio into clear, summarized notes.</div>", unsafe_allow_html=True)

# ----------------------- Audio Upload Section -----------------------
uploaded_audio = st.file_uploader("Upload your meeting audio file", type=["mp3", "wav", "m4a"])

if uploaded_audio:
    st.audio(uploaded_audio, format="audio/mp3")
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_audio.read())
    audio_path = temp_file.name

    if st.button("Generate Notes"):
        try:
            with st.spinner("Transcribing audio using Whisper..."):
                transcript_data = openai.Audio.transcriptions.create(
                    model="whisper-1",
                    file=open(audio_path, "rb")
                )
                transcript = transcript_data.text

            st.success("Transcription complete.")

            with st.spinner("Summarizing notes using GPT..."):
                summary_prompt = (
                    "Summarize the following meeting transcript in bullet points, "
                    "highlighting key decisions, action items, and important discussion points.\n\n"
                    f"{transcript}"
                )

                summary_response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": summary_prompt}],
                )

                summary = summary_response.choices[0].message.content.strip()

            st.success("Summary generated successfully.")

            # ----------------------- Display Results -----------------------
            st.subheader("Transcription")
            st.text_area("", transcript, height=200)

            st.subheader("Meeting Summary")
            st.text_area("", summary, height=200)

            # ----------------------- Download Button -----------------------
            summary_bytes = BytesIO(summary.encode("utf-8"))
            st.download_button(
                label="Download Summary as .txt",
                data=summary_bytes,
                file_name="meeting_summary.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Always remove temporary files after use
            try:
                os.remove(audio_path)
            except Exception:
                pass

# ----------------------- Footer -----------------------
st.markdown("<footer>Developed with care and the grace of Allah.</footer>", unsafe_allow_html=True)
