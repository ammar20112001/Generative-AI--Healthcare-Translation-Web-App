# Healthcare Translation App

[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/ammar-20112001/Medical-Translator)  
*Note: Due to limitations on cloud server deployments, the microphone functionality is not available on the hosted version. The app can only transcribe and translate uploaded audio files. For full functionality, please follow the local setup instructions below.*

---

## 🔧 Tech Stack

Python, Streamlit, Google Cloud Speech-to-Text, Google Cloud Text-to-Speech  
OpenAI GPT, Hugging Face Spaces, Docker, Git, GitHub  

<div align="center">
  <img src="https://img.icons8.com/color/48/000000/python.png" alt="Python" height="40"/>
  <img src="https://i.ibb.co/z55CzGz/streamlit-logo.png" alt="Streamlit" height="50"/>
  <img src="https://img.icons8.com/fluency/48/000000/google-cloud.png" alt="Google Cloud" height="40"/>
  <img src="https://i.ibb.co/thdPt0w/openai-chatgpt-logo.webp" alt="OpenAI GPT" height="40"/>
  <img src="https://i.ibb.co/BzLrJQ2/hf-logo.png" height="40" alt="transformers logo"  />
  <img src="https://img.icons8.com/fluency/48/000000/docker.png" alt="Docker" height="40"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" height="40" alt="git logo"  />
</div>

---

## Overview

The **Healthcare Translation App** is a powerful tool designed to assist healthcare professionals in multilingual environments. It uses state-of-the-art AI technology to transcribe speech, translate it into a target language, and convert the translated text back into speech in real-time.

### Key Features:
- **Speech-to-Text**: Transcribes spoken language into text using Google Cloud Speech-to-Text.
- **Text Translation**: Translates the transcribed text into a target language using OpenAI GPT.
- **Text-to-Speech**: Converts the translated text back into speech using Google Cloud Text-to-Speech.
- **Audio File Upload**: Upload MP3 or WAV files to be transcribed and translated.
- **Language Selection**: Supports multiple source and target languages for both transcription and translation.
  
This app is designed to help healthcare workers communicate more effectively across different languages, making it an invaluable tool in diverse and fast-paced medical environments.

---

## Deployed Version

You can try the **Healthcare Translation App** hosted on Hugging Face Spaces:  
[Healthcare Translation App - Live Demo](https://huggingface.co/spaces/ammar-20112001/Medical-Translator)

*Important Note*: Due to the limitations of cloud server environments, the hosted version cannot access the microphone. Therefore, it only supports the upload of audio files for transcription and translation. If you want to use the full functionality, please follow the instructions below to set up the app locally.

---

## Local Setup & Installation

To run the **Healthcare Translation App** locally and access all features (including microphone support), follow these steps:

### Prerequisites

- **Python 3.7+**: Ensure Python is installed on your local machine.
- **Google Cloud Account**: You will need a Google Cloud account with access to the Speech-to-Text and Text-to-Speech APIs. Download your credentials (in JSON format).
- **OpenAI API Key**: You'll need an API key from OpenAI to handle text translation.
- **Streamlit**: Used to create the app’s web interface.

### Setup Steps

1. **Clone the Repository**:
   Open your terminal and run the following command to clone the repository:
   ```bash
   git clone https://github.com/your-username/Healthcare-Translation-App.git
   cd Healthcare-Translation-App
   ```
2. **Create a Virtual Environment**:
   Install the required Python libraries by running:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate
   ```
3. **Install Dependencies**:
   It's best to create a virtual environment to manage dependencies. Run:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up Environment Variables**:
   In the project directory, create a .env file to store your API keys and credentials. Add the following variables to the .env file:
      - **OPENAI_API_KEY**: Your OpenAI API key.
      - **GCP_KEY**: The path to your Google Cloud service account credentials (JSON file).
    Example .env file:
     ```bash
     OPENAI_API_KEY=your_openai_api_key_here
     GCP_KEY='your_google_cloud_service_account_json_here'
     ```
5. **Run the Application**: Launch the app using Streamlit by running the following command:
    ```bash
     streamlit run app.py
     ```
6. **Access the App**: After running the above command, open your browser and visit http://localhost:8501 to access the app.

---

## How to Use the App

### **Language Selection**:
1. **Select the source language**: This is the language you want to transcribe from. You can choose from a variety of languages.
2. **Select the target language**: Choose the language you want to translate the transcribed text into. The app supports a wide range of languages for translation.

### **Real-Time Recording**:
1. **Click "Start Real-Time Recording"** to begin transcribing audio from your microphone. The app will listen to the spoken language in real-time and begin transcribing it into text.
2. Once the speech is transcribed, the app will translate the text into your selected target language.
3. The translated text will then be converted back into speech using the Google Cloud Text-to-Speech API, and you will hear the translated audio in real-time.
4. **Click "Stop Real-Time Recording"** to end the recording session.

### **File Upload**:
1. **Click "Upload an audio file"** to upload an MP3 or WAV file for transcription and translation.
2. Once the file is uploaded, the app will transcribe the audio, translate the transcribed text into the target language, and convert the translated text back into speech.
3. **Click "Play Audio"** to listen to the translated speech.

### **Clear Transcripts**:
1. **Click "Clear"** to reset both the source and target language transcripts. This will erase any previously transcribed or translated text.

### **Play Audio**:
1. After the translation is complete, you can click the **"Play Audio"** button to hear the translated text spoken aloud.
2. The app uses Google Cloud Text-to-Speech to convert the translated text into a natural-sounding voice, allowing you to hear the translation as it would be spoken by a native speaker.

---

## Technologies Used

### **APIs**:
- **Google Speech-to-Text**: For transcribing spoken language into text.
- **OpenAI API**: For translating text from the source language to the target language.
- **Google Text-to-Speech**: For converting the translated text back into audio.

### **Web Service**:
- **Streamlit**: The app's front-end framework for building interactive web applications.

### **Hosting Services**:
- **Hugging Face Spaces**: For hosting the application.
- **Streamlit Cloud**: For deployment of the app.

### **Version Control**:
- **Git**: For version control.
- **GitHub**: For code hosting and collaboration.

### **Real-Time Transcription/Translation**:
- **Multi-threading**: The application uses threading to handle real-time audio transcription and translation simultaneously.

---

## Application Deployment

The app has been deployed on [Hugging Face Spaces](https://huggingface.co/spaces/ammar-20112001/Medical-Translator).

> **Note:** Due to cloud server limitations, microphone access is not available, and thus the app can only process uploaded audio files on Hugging Face Spaces. For full functionality, including real-time speech-to-text and translation, we recommend setting up the app locally.

---

## How to Set Up Locally

To run the app locally and access all its features, follow these steps:

### **Requirements**:
- Python 3.x
- A virtual environment (recommended)
- Dependencies listed in the `requirements.txt` file

### **Installation Steps**:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repository-url.git
    cd your-repository-folder
    ```

2. **Set Up a Virtual Environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
    - You will need to set up environment variables for your Google Cloud and OpenAI API keys.
    - Create a `.env` file in the project directory and add the following variables:

    ```env
    OPENAI_API_KEY_MEDICAL_TRANSLATOR=your_openai_api_key
    GCP_KEY_MEDICAL_TRANSLATOR=your_google_cloud_credentials_json_string
    ```

    You can obtain the `GCP_KEY_MEDICAL_TRANSLATOR` from the [Google Cloud Console](https://console.cloud.google.com/).

5. **Run the App**:
    ```bash
    streamlit run app.py
    ```

6. Open your browser and visit the URL shown in the terminal to interact with the app locally.

---

## Acknowledgments

- Thanks to **Google Cloud** for their Speech-to-Text and Text-to-Speech APIs.
- Thanks to **OpenAI** for providing the GPT model for translation.
- Thanks to **Streamlit** for making web app development so easy and interactive.

---

Enjoy using the Healthcare Translation App and feel free to contribute!
