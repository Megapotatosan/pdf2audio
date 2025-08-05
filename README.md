# 📄➡️🔊 PDF to Audio Converter (OpenAI TTS)

A Python application that converts PDF documents to high-quality audio using OpenAI's TTS-1-HD text-to-speech API, with a user-friendly Gradio interface. Supports multiple voices and long documents.

---

## 🌟 Features

- **OpenAI TTS Integration**: Uses OpenAI's TTS-1-HD model for premium, natural-sounding speech
- **Multiple Voices**: Choose from 6 different voice options (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- **PDF Text Extraction**: Automatically extracts text from uploaded PDF files
- **Web Interface**: Clean and intuitive Gradio-based GUI
- **Audio Download**: Generated audio files can be downloaded as WAV files
- **Text Preview**: View extracted text before conversion
- **Long Document Support**: Handles large PDFs with intelligent text chunking

---

## 🛠️ Requirements

- Python 3.8 or higher
- OpenAI account and API key ([get one here](https://platform.openai.com/api-keys))
- At least 4GB of RAM
- Internet connection (for API access and model inference)

**Python Packages:**
- gradio
- openai
- PyPDF2
- soundfile
- numpy
- requests

Install all dependencies with the provided requirements.txt.

---

## 📦 Installation

1. **Clone or download this repository**
2. **Navigate to the project directory**
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

1. **Start the application:**
   ```bash
   python pdf_to_audio.py
   ```

2. **Open your browser** and go to:
   ```
   http://127.0.0.1:7860
   ```

3. **Enter your OpenAI API key** in the provided field and click "Set API Key".

4. **Upload a PDF file** using the file upload interface.

5. **Select a voice** from the dropdown menu.

6. **Click "Convert to Audio"** to process the PDF.

7. **Listen to the generated audio** and download if needed.

---

## 🎭 Voice Options

- **Alloy**: Neutral, balanced voice suitable for most content
- **Echo**: Clear male voice with good articulation
- **Fable**: British-accented male voice, great for storytelling
- **Onyx**: Deep, authoritative male voice
- **Nova**: Clear, professional female voice
- **Shimmer**: Warm, friendly female voice

---

## 🔧 Technical Details

- **Text-to-Speech**: OpenAI TTS-1-HD model via OpenAI API
- **Text Chunking**: Automatically splits long text into 4000-character chunks for processing
- **Audio Format**: Output is WAV (concatenated from MP3 chunks)
- **Sample Rate**: 16kHz (standard for speech)
- **Channels**: Mono
- **API Key**: Required for all conversions; not stored permanently

---

## ⚙️ Configuration

- **Text Length**: Each chunk is limited to 4000 characters for OpenAI TTS API compatibility
- **Voice Selection**: Choose from 6 voices in the interface
- **API Key**: Enter your OpenAI API key at startup; required for all conversions

---

## 📁 Project Structure

```
pdf2audio/
├── pdf_to_audio.py      # Main application file
├── requirements.txt     # Python dependencies
├── setup.py             # (Optional) Setup script
└── README.md            # This file
```

---

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your API key is correct and active
   - Check your OpenAI account for usage limits or billing issues

2. **PDF Reading Errors**:
   - Ensure PDF contains extractable text (not scanned images)
   - Try with different PDF files

3. **Audio Generation Fails**:
   - Check if text contains special characters
   - Ensure your internet connection is stable

4. **Long Processing Time**:
   - Large PDFs may take several minutes to process
   - Processing time depends on document length and API response speed

### Performance Tips

- **Text Length**: Keep PDFs concise for faster processing
- **Memory Management**: Close other applications if running low on memory

---

## 🔄 Updates and Maintenance

- To update dependencies:
  ```bash
  pip install -r requirements.txt --upgrade
  ```
- The application uses the latest OpenAI TTS API; check [OpenAI documentation](https://platform.openai.com/docs/guides/text-to-speech) for updates.

---

## 📝 License

This project uses the following open-source components:
- Gradio (Apache 2.0)
- OpenAI Python SDK (MIT)
- PyPDF2 (BSD-3-Clause)
- soundfile (BSD)
- numpy (BSD)
- requests (Apache 2.0)

---

## 🤝 Contributing

Contributions are welcome! Submit issues, feature requests, or pull requests to improve this application.

---

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Check console output for error messages
4. Ensure PDF files contain extractable text
5. Ensure your OpenAI API key is valid and active

---

## 🎯 Future Enhancements

- Support for additional audio formats (MP3, OGG, etc.)
- Batch processing of multiple PDFs
- Speed and pitch control
- Chapter/section-based audio splitting
- Customizable chunk size and pause duration
