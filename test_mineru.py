#!/usr/bin/env python3
"""
Test script to verify MinerU API integration
"""

from urllib import response
import requests
import json

def test_mineru_api():
    """Test the MinerU API endpoint"""
    try:
        url = 'http://localhost:8000/file_parse'

        files = {
            'files': ('Chapter 3 - Basic Selfhood.pdf', open('Chapter 3 - Basic Selfhood.pdf', 'rb'), 'application/pdf'),
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
            # DO NOT set Content-Type for multipart requests; requests handles that!
        }

        response = requests.post(url, data=data, files=files, headers=headers)
        print(response.status_code)
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ MinerU API connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MinerU API Integration")
    print("=" * 50)
    test_mineru_api()
    print("\n✨ Integration test completed!")
    print("\n📝 Note: To test with actual PDF files, upload them through the web interface")
    print("🌐 Start the application with: python pdf_to_audio.py")
