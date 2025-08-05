import gradio as gr
import soundfile as sf
import numpy as np
import tempfile
import os
from typing import Optional, Tuple
import openai
import requests
from pathlib import Path
import json

class PDFToAudioConverter:
    def __init__(self):
        """Initialize the PDF to Audio converter with OpenAI TTS."""
        self.client = None
        self.api_key = None
        print("PDF to Audio Converter initialized. Please provide your OpenAI API key.")
        
    def set_api_key(self, api_key: str) -> str:
        """Set the OpenAI API key and initialize the client."""
        try:
            if not api_key or not api_key.strip():
                return "❌ Please provide a valid OpenAI API key."
            
            self.api_key = api_key.strip()
            self.client = openai.OpenAI(api_key=self.api_key)
            
            # Test the API key with a simple request
            try:
                # Test with a very short text
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input="Test"
                )
                return "✅ OpenAI API key validated successfully! Ready to convert PDFs to audio."
            except Exception as e:
                self.client = None
                self.api_key = None
                return f"❌ Invalid API key or API error: {str(e)}"
                
        except Exception as e:
            return f"❌ Error setting API key: {str(e)}"
    
    def extract_text_from_pdf_mineru(self, pdf_file) -> str:
        """Extract text content from uploaded PDF file using MinerU API."""
        try:
            if pdf_file is None:
                return "No PDF file provided."
            
            print("🔄 Using MinerU API for advanced PDF parsing...")
            
            # Prepare the file for upload to MinerU API
            with open(pdf_file, 'rb') as f:
                files = {
                    'files': (os.path.basename(pdf_file), f, 'application/pdf'),
                }

                data = {
                    'return_middle_json': 'false',
                    'return_model_output': 'false',
                    'return_md': 'true',
                    'return_images': 'false',
                    'end_page_id': '99999',
                    'parse_method': 'auto',
                    'start_page_id': '0',
                    'lang_list': 'ch',
                    'output_dir': '',
                    'server_url': 'string',
                    'return_content_list': 'false',
                    'backend': 'pipeline',
                    'table_enable': 'true',
                    'formula_enable': 'true',
                }

                
                headers = {
                    'accept': 'application/json'
                }
                # Make request to MinerU API
                response = requests.post(
                    #url of MinerU API endpoint
                    "http://localhost:8000/file_parse",
                    headers=headers,
                    data=data,
                    files=files
                    #timeout=120  # 2 minutes timeout for large files
                )
            
            if response.status_code != 200:
                print(f"❌ MinerU API error: {response.status_code}")
                # Fallback to basic extraction if MinerU fails
                return self.extract_text_from_pdf_fallback(pdf_file)
            
            # Parse the response
            try:
                result = response.json()
                
                # Extract text from MinerU response
                if 'markdown' in result:
                    # MinerU returns markdown format
                    markdown_text = result['markdown']
                    # Convert markdown to plain text for TTS
                    cleaned_text = self.clean_markdown_text(markdown_text)
                elif 'text' in result:
                    # Direct text response
                    cleaned_text = result['text']
                else:
                    # Try to extract from any text field in the response
                    cleaned_text = str(result)
                
                if not cleaned_text or not cleaned_text.strip():
                    print("⚠️ MinerU returned empty text, falling back to basic extraction")
                    return self.extract_text_from_pdf_fallback(pdf_file)
                
                print(f"✅ MinerU PDF extraction completed successfully! Extracted {len(cleaned_text)} characters with advanced parsing.")
                return cleaned_text.strip()
                
            except json.JSONDecodeError:
                # If response is not JSON, treat as plain text
                cleaned_text = response.text
                if cleaned_text and cleaned_text.strip():
                    print(f"✅ MinerU PDF extraction completed! Extracted {len(cleaned_text)} characters.")
                    return cleaned_text.strip()
                else:
                    print("⚠️ MinerU returned empty response, falling back to basic extraction")
                    return self.extract_text_from_pdf_fallback(pdf_file)
                    
        except requests.exceptions.Timeout:
            print("⚠️ MinerU API timeout, falling back to basic extraction")
            return self.extract_text_from_pdf_fallback(pdf_file)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ MinerU API connection error: {str(e)}, falling back to basic extraction")
            return self.extract_text_from_pdf_fallback(pdf_file)
        except Exception as e:
            print(f"⚠️ MinerU processing error: {str(e)}, falling back to basic extraction")
            return self.extract_text_from_pdf_fallback(pdf_file)

    def extract_text_from_pdf_fallback(self, pdf_file) -> str:
        """Fallback PDF extraction method using basic text extraction."""
        try:
            print("🔄 Using fallback PDF extraction method...")
            
            # Simple text extraction without PyPDF2 dependency
            import fitz  # PyMuPDF - more reliable than PyPDF2
            
            doc = fitz.open(pdf_file)
            all_pages_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    all_pages_text.append(page_text)
            
            doc.close()
            
            if not all_pages_text:
                return "No text found in the PDF file."
            
            # Basic text cleaning
            full_text = "\n".join(all_pages_text)
            cleaned_text = self.basic_text_cleaning(full_text)
            
            if not cleaned_text.strip():
                return "No meaningful text found after processing."
            
            print(f"✅ Fallback PDF extraction completed! Extracted {len(cleaned_text)} characters from {len(all_pages_text)} pages.")
            return cleaned_text.strip()
            
        except ImportError:
            return "PDF extraction failed. Please install PyMuPDF: pip install PyMuPDF"
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    def clean_markdown_text(self, markdown_text: str) -> str:
        """Convert markdown text to clean plain text suitable for TTS."""
        import re
        
        if not markdown_text:
            return ""
        
        # Remove markdown formatting
        text = markdown_text
        
        # Remove headers (# ## ###)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold and italic markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
        text = re.sub(r'__(.*?)__', r'\1', text)      # __bold__
        text = re.sub(r'_(.*?)_', r'\1', text)        # _italic_
        
        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
        text = re.sub(r'<([^>]+)>', r'\1', text)               # <url>
        
        # Remove code blocks and inline code
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)  # ```code```
        text = re.sub(r'`([^`]+)`', r'\1', text)                  # `code`
        
        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # - * +
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE) # 1. 2. 3.
        
        # Remove horizontal rules
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)
        
        # Remove blockquotes
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'\n{3,}', '\n\n', text)   # More than 2 newlines to 2
        text = re.sub(r'[ \t]+', ' ', text)      # Multiple spaces to single
        
        # Convert newlines to spaces for better TTS flow
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def basic_text_cleaning(self, text: str) -> str:
        """Basic text cleaning for fallback extraction."""
        import re
        
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\'\"]', ' ', text)
        
        # Clean up extra spaces
        text = " ".join(text.split())
        
        return text.strip()

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Main PDF extraction method - tries MinerU first, falls back if needed."""
        return self.extract_text_from_pdf_mineru(pdf_file)
    
    def clean_pdf_text(self, pages_text: list) -> str:
        """Clean PDF text by removing headers, footers, and improving readability."""
        import re
        
        if not pages_text:
            return ""
        
        # Combine all pages
        full_text = "\n".join(pages_text)
        
        # Split into lines for processing
        lines = full_text.split('\n')
        cleaned_lines = []
        
        # Remove empty lines and very short lines that might be artifacts
        lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 2]
        
        if not lines:
            return ""
        
        # Detect and remove potential headers/footers
        # Headers/footers often repeat across pages or contain page numbers
        line_frequency = {}
        for line in lines:
            # Normalize line for comparison (remove numbers that might be page numbers)
            normalized = re.sub(r'\b\d+\b', '', line).strip()
            if len(normalized) > 5:  # Only consider substantial lines
                line_frequency[normalized] = line_frequency.get(normalized, 0) + 1
        
        # Lines that appear frequently might be headers/footers
        total_pages = len(pages_text)
        frequent_lines = set()
        for normalized_line, count in line_frequency.items():
            # If a line appears in more than 30% of pages, it might be header/footer
            if count > max(2, total_pages * 0.3):
                frequent_lines.add(normalized_line)
        
        # Filter out likely headers/footers and page numbers
        for line in lines:
            # Skip lines that are likely page numbers
            if re.match(r'^\s*\d+\s*$', line):
                continue
            
            # Skip lines that are very short and contain mostly numbers/symbols
            if len(line) < 10 and re.match(r'^[\d\s\-\.\|]+$', line):
                continue
            
            # Check if this line is a frequent header/footer
            normalized = re.sub(r'\b\d+\b', '', line).strip()
            if normalized in frequent_lines and len(normalized) < 50:
                continue
            
            # Skip lines that look like URLs or email addresses (often in footers)
            if re.search(r'(https?://|www\.|@.*\.com)', line, re.IGNORECASE):
                continue
            
            # Skip copyright notices and similar footer content
            if re.search(r'(copyright|©|\(c\)|all rights reserved)', line, re.IGNORECASE):
                continue
            
            cleaned_lines.append(line)
        
        # Join cleaned lines and perform additional text processing
        cleaned_text = ' '.join(cleaned_lines)
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Fix common PDF extraction issues
        # Remove hyphenation at line breaks
        cleaned_text = re.sub(r'-\s+', '', cleaned_text)
        
        # Fix spacing around punctuation
        cleaned_text = re.sub(r'\s+([,.!?;:])', r'\1', cleaned_text)
        cleaned_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', cleaned_text)
        
        return cleaned_text.strip()
    
    def split_text_into_chunks(self, text: str, max_length: int = 4000) -> list:
        """Split long text into manageable chunks for OpenAI TTS processing."""
        # Clean the text first
        import re
        text = " ".join(text.split())
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\'\"]', ' ', text)
        text = " ".join(text.split())
        
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Get a chunk of max_length
            end_pos = min(current_pos + max_length, len(text))
            chunk = text[current_pos:end_pos]
            
            # If this isn't the last chunk, try to end at a sentence boundary
            if end_pos < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(0, len(chunk) - 200)
                last_period = chunk.rfind('.', search_start)
                last_exclamation = chunk.rfind('!', search_start)
                last_question = chunk.rfind('?', search_start)
                
                sentence_end = max(last_period, last_exclamation, last_question)
                if sentence_end > 0:
                    chunk = chunk[:sentence_end + 1]
                    current_pos += sentence_end + 1
                else:
                    # If no sentence ending found, look for word boundary
                    last_space = chunk.rfind(' ', search_start)
                    if last_space > 0:
                        chunk = chunk[:last_space]
                        current_pos += last_space + 1
                    else:
                        current_pos = end_pos
            else:
                current_pos = end_pos
            
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks

    def clean_text_for_tts(self, text: str) -> str:
        """Clean and prepare text for text-to-speech conversion."""
        # Remove excessive whitespace and newlines
        text = " ".join(text.split())
        
        # Remove problematic characters but keep more natural punctuation
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\'\"]', ' ', text)
        text = " ".join(text.split())  # Clean up extra spaces
        
        return text
    
    def text_to_speech_chunk(self, text_chunk: str, voice: str = "alloy") -> Optional[str]:
        """Convert a single text chunk to speech using OpenAI TTS and return temp file path."""
        try:
            if not text_chunk or not text_chunk.strip():
                return None
            
            if not self.client:
                print("OpenAI client not initialized. Please set API key first.")
                return None
            
            # Clean text
            clean_text = self.clean_text_for_tts(text_chunk)
            
            # OpenAI TTS can handle up to 4096 characters
            if len(clean_text) > 4000:
                clean_text = clean_text[:4000]
                # Try to end at a word boundary
                last_space = clean_text.rfind(' ')
                if last_space > 3800:
                    clean_text = clean_text[:last_space]
            
            # Generate speech using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1-hd",  # Use high-definition model for better quality
                voice=voice,
                input=clean_text,
                response_format="mp3"
            )
            
            # Create temporary file for this chunk
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating audio for chunk: {str(e)}")
            return None

    def text_to_speech(self, text: str, voice: str = "alloy") -> Tuple[Optional[str], str]:
        """Convert text to speech using OpenAI TTS with chunking for long texts."""
        try:
            if not text or not text.strip():
                return None, "No text provided for conversion."
            
            if not self.client:
                return None, "OpenAI API key not set. Please provide your API key first."
            
            # Split text into chunks for OpenAI TTS (can handle up to 4096 characters)
            text_chunks = self.split_text_into_chunks(text, max_length=4000)
            print(f"Processing {len(text_chunks)} text chunks with OpenAI TTS...")
            
            # Generate audio for each chunk
            audio_files = []
            for i, chunk in enumerate(text_chunks):
                print(f"Processing chunk {i+1}/{len(text_chunks)}")
                audio_file = self.text_to_speech_chunk(chunk, voice)
                if audio_file is not None:
                    audio_files.append(audio_file)
            
            if not audio_files:
                return None, "Failed to generate audio for any text chunks."
            
            # Load and concatenate all audio files
            audio_segments = []
            sample_rate = None
            
            for audio_file in audio_files:
                try:
                    audio_data, sr = sf.read(audio_file)
                    if sample_rate is None:
                        sample_rate = sr
                    
                    # Ensure audio is mono
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)
                    
                    audio_segments.append(audio_data)
                    
                    # Add a small pause between chunks (0.5 seconds of silence)
                    if audio_file != audio_files[-1]:  # Don't add pause after last chunk
                        silence = np.zeros(int(0.5 * sample_rate))
                        audio_segments.append(silence)
                    
                    # Clean up temporary file
                    os.unlink(audio_file)
                except Exception as e:
                    print(f"Error reading audio file {audio_file}: {e}")
                    continue
            
            if not audio_segments:
                return None, "Failed to process any audio segments."
            
            # Concatenate all audio segments
            full_audio = np.concatenate(audio_segments)
            
            # Create final temporary audio file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(temp_file.name, full_audio, samplerate=sample_rate)
            
            duration = len(full_audio) / sample_rate  # Calculate duration in seconds
            print(f"🎵 Audio generation completed successfully! Generated {duration:.1f} seconds of audio from {len(text_chunks)} text chunks.")
            return temp_file.name, f"🎉 High-quality audio generated successfully using OpenAI TTS! Duration: {duration:.1f} seconds ({len(text_chunks)} chunks processed)"
            
        except Exception as e:
            error_msg = f"Error generating audio: {str(e)}"
            print(error_msg)
            return None, error_msg
    
    def process_pdf_to_audio(self, pdf_file, voice) -> Tuple[Optional[str], str, str]:
        """Main function to process PDF file and convert to audio."""
        try:
            if not self.client:
                return None, "", "❌ Please set your OpenAI API key first."
            
            # Extract text from PDF
            extracted_text = self.extract_text_from_pdf(pdf_file)
            
            if extracted_text.startswith("Error") or extracted_text.startswith("No"):
                return None, extracted_text, extracted_text
            
            # Convert text to speech
            audio_file, status_message = self.text_to_speech(extracted_text, voice)
            
            if audio_file:
                print("🎊 PDF to Audio conversion process completed successfully!")
                print("=" * 60)
            
            return audio_file, extracted_text, status_message
            
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            return None, "", error_msg

def create_gradio_interface():
    """Create and configure the Gradio interface."""
    
    # Initialize converter
    converter = PDFToAudioConverter()
    
    # Define the interface
    with gr.Blocks(title="PDF to Audio Converter - OpenAI TTS", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 📄➡️🔊 PDF to Audio Converter (OpenAI TTS + MinerU)
            
            Upload a PDF file and convert its text content to speech using OpenAI's state-of-the-art TTS API with advanced MinerU PDF parsing.
            
            **Features:**
            - 🚀 **MinerU Integration**: Advanced PDF parsing for complex layouts, scientific documents, and better text extraction
            - 🎯 **Premium Quality**: Uses OpenAI's TTS-1-HD model for superior audio quality
            - 📖 **Smart PDF Extraction**: Automatically extracts text with structure preservation and header/footer removal
            - 🎭 **Multiple Voices**: Choose from 6 different voice options
            - 📚 **Long Document Support**: Processes entire PDF chapters with intelligent chunking
            - 💾 **Download Audio**: Generated audio files can be downloaded as WAV files
            - 👀 **Text Preview**: View extracted text before conversion
            - 🔄 **Fallback System**: Automatic fallback if MinerU API is unavailable
            """
        )
        
        # API Key Section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔑 OpenAI API Configuration")
                api_key_input = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="Enter your OpenAI API key (sk-...)",
                    type="password",
                    info="Your API key is required to use OpenAI's TTS service. It's not stored permanently."
                )
                api_key_btn = gr.Button("🔐 Set API Key", variant="secondary")
                api_status = gr.Textbox(
                    label="API Status",
                    interactive=False,
                    value="⏳ Please provide your OpenAI API key to get started."
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("### 📤 Upload & Configure")
                pdf_input = gr.File(
                    label="Select PDF File",
                    file_types=[".pdf"],
                    type="filepath"
                )
                
                voice_input = gr.Dropdown(
                    label="🎭 Select Voice",
                    choices=[
                        ("Alloy (Neutral)", "alloy"),
                        ("Echo (Male)", "echo"), 
                        ("Fable (British Male)", "fable"),
                        ("Onyx (Deep Male)", "onyx"),
                        ("Nova (Female)", "nova"),
                        ("Shimmer (Female)", "shimmer")
                    ],
                    value="alloy",
                    info="Choose the voice for your audio"
                )
                
                convert_btn = gr.Button(
                    "🎵 Convert to Audio",
                    variant="primary",
                    size="lg"
                )
                
                # Status display
                status_output = gr.Textbox(
                    label="Conversion Status",
                    interactive=False,
                    lines=3
                )
            
            with gr.Column(scale=1):
                # Output section
                gr.Markdown("### 🎧 Generated Audio")
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="filepath"
                )
                
                # Text preview
                gr.Markdown("### 📝 Extracted Text Preview")
                text_output = gr.Textbox(
                    label="PDF Text Content",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    show_copy_button=True
                )
        
        # Event handlers
        api_key_btn.click(
            fn=converter.set_api_key,
            inputs=[api_key_input],
            outputs=[api_status]
        )
        
        convert_btn.click(
            fn=converter.process_pdf_to_audio,
            inputs=[pdf_input, voice_input],
            outputs=[audio_output, text_output, status_output],
            show_progress=True
        )
        
        # Information section
        gr.Markdown(
            """
            ### 💡 Usage Tips:
            - **API Key**: Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
            - **Supported Format**: PDF files only (text-based, not scanned images)
            - **Voice Quality**: TTS-1-HD model provides the highest quality audio
            - **Processing Time**: Large PDFs may take a few minutes to process
            - **Cost**: Uses OpenAI's TTS API (check current pricing on OpenAI's website)
            
            ### 🎭 Voice Descriptions:
            - **Alloy**: Neutral, balanced voice suitable for most content
            - **Echo**: Clear male voice with good articulation  
            - **Fable**: British-accented male voice, great for storytelling
            - **Onyx**: Deep, authoritative male voice
            - **Nova**: Clear, professional female voice
            - **Shimmer**: Warm, friendly female voice
            """
        )
    
    return interface

def main():
    """Main function to launch the application."""
    print("Starting PDF to Audio Converter with OpenAI TTS...")
    
    try:
        # Create and launch interface
        interface = create_gradio_interface()
        
        # Launch with specific configuration
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        print(f"Error launching application: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
