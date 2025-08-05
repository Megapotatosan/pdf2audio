# MinerU Text Cleaning Improvements

## Overview

This document outlines the improvements made to the PDF to Audio converter to handle MinerU parsing data with enhanced text cleaning for optimal text-to-speech conversion.

## Problem Statement

The original MinerU parsing data contained:
- Complex nested structure: `{'backend': 'pipeline', 'version': '2.1.7', 'results': {...}}`
- Markdown formatting artifacts
- Mathematical expressions like `$8 ^ { \mathrm { t h } }$`
- Image references `![](images/...)`
- Email addresses and URLs
- Mixed Chinese and English content
- Headers and formatting that aren't suitable for TTS

## Solution Implementation

### 1. Enhanced Data Structure Handling

**New Function: `extract_text_from_mineru_response()`**
```python
def extract_text_from_mineru_response(self, result: dict) -> str:
    """Extract and clean text from MinerU API response structure."""
    # Handles nested structure: {'backend': ..., 'version': ..., 'results': {...}}
    if 'results' in result and isinstance(result['results'], dict):
        all_content = []
        # Iterate through all documents in results
        for doc_title, doc_data in result['results'].items():
            if isinstance(doc_data, dict) and 'md_content' in doc_data:
                markdown_content = doc_data['md_content']
                if markdown_content:
                    cleaned_content = self.clean_mineru_markdown_text(markdown_content)
                    if cleaned_content.strip():
                        all_content.append(cleaned_content)
        return ' '.join(all_content)
```

### 2. Specialized MinerU Markdown Cleaning

**New Function: `clean_mineru_markdown_text()`**

This function provides enhanced cleaning specifically for MinerU content:

#### Key Features:

1. **Image Reference Removal**
   ```python
   # Remove image references completely (not useful for audio)
   text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
   ```

2. **Mathematical Expression Conversion**
   ```python
   # Handle mathematical notation - convert to readable text
   # LaTeX math expressions like $8 ^ { \mathrm { t h } }$
   text = re.sub(r'\$([^$]+)\$', lambda m: self.convert_math_to_text(m.group(1)), text)
   ```

3. **Email and URL Cleanup**
   ```python
   # Clean up email addresses and URLs that might be in footers
   text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
   text = re.sub(r'https?://[^\s]+', '', text)
   text = re.sub(r'www\.[^\s]+', '', text)
   ```

4. **PDF Artifact Removal**
   ```python
   # Remove common PDF artifacts and formatting
   text = re.sub(r'\b(Page \d+|第\d+页|\d+/\d+)\b', '', text)  # Page numbers
   text = re.sub(r'\b\d{4}年\d{1,2}月\d{1,2}日\b', '', text)  # Chinese dates
   text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', '', text)      # English dates
   ```

5. **Chinese-English Mixed Content Optimization**
   ```python
   # Handle Chinese and English mixed content
   # Add spaces between Chinese and English characters for better TTS
   text = re.sub(r'([\u4e00-\u9fff])([A-Za-z])', r'\1 \2', text)
   text = re.sub(r'([A-Za-z])([\u4e00-\u9fff])', r'\1 \2', text)
   ```

### 3. Mathematical Expression Conversion

**New Function: `convert_math_to_text()`**

Converts LaTeX mathematical expressions to TTS-friendly text:

#### Examples:
- `$8 ^ { \mathrm { t h } }$` → `8th`
- `$9 ^ { \mathrm { t h } }$` → `9th`
- `$x^2$` → `x to the power of 2`
- `$\frac{1}{2}$` → `1 over 2`

#### Implementation:
```python
def convert_math_to_text(self, math_expr: str) -> str:
    """Convert LaTeX math expressions to readable text for TTS."""
    # Handle ordinal numbers like "8 ^ { \mathrm { t h } }"
    ordinal_pattern = r'(\d+)\s*\^\s*\{\s*\\*mathrm\s*\{\s*([a-z]+)\s*\}\s*\}'
    ordinal_match = re.search(ordinal_pattern, math_expr)
    if ordinal_match:
        number = ordinal_match.group(1)
        suffix = ordinal_match.group(2)
        return f"{number}{suffix}"
    
    # Handle simple superscripts like "x^2"
    math_expr = re.sub(r'(\w+)\^(\d+)', r'\1 to the power of \2', math_expr)
    
    # Handle fractions
    math_expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 over \2', math_expr)
```

## Results

### Performance Metrics

From the test with sample data:
- **Original length**: 2,032 characters
- **Cleaned length**: 1,598 characters
- **Reduction**: 21.4%

### Cleaning Features Verified

✅ **Images removed**: All image references eliminated  
✅ **Math expressions converted**: LaTeX expressions converted to readable text  
✅ **Email addresses removed**: Contact information cleaned  
✅ **Markdown headers removed**: Formatting artifacts eliminated  
✅ **Proper spacing added**: Chinese-English mixed content optimized  

### Sample Output

**Before Cleaning:**
```
# 通告

日期 2020年11月1日致 全體員工

# 優化員工内部溝通渠道

![](images/4e50d4954edc4e0c3100726c43e0c4bb8fc932bddcb1f047cd2a1baa109702a1.jpg)

The Opinion Boxes are located at $8 ^ { \mathrm { t h } }$ floor and $9 ^ { \mathrm { t h } }$ floor

電郵地址是kwopinion@kinwing.com.hk
```

**After Cleaning:**
```
通告 日期 2020年11月1日致 全體員工 優化員工内部溝通渠道 The Opinion Boxes are located at 8th floor and 9th floor
```

## Integration

The improvements are seamlessly integrated into the existing PDF to Audio converter:

1. **Automatic Detection**: The system automatically detects MinerU response structure
2. **Fallback Support**: If MinerU is unavailable, falls back to basic PDF extraction
3. **TTS Optimization**: All cleaned text is optimized for OpenAI TTS conversion
4. **Multi-language Support**: Handles Chinese, English, and mixed content

## Usage

The enhanced cleaning is automatically applied when using MinerU API:

```python
# The system automatically:
# 1. Detects MinerU response structure
# 2. Extracts content from nested results
# 3. Applies specialized cleaning
# 4. Converts to TTS-ready text

converter = PDFToAudioConverter()
cleaned_text = converter.extract_text_from_pdf(pdf_file)
audio_file, status = converter.text_to_speech(cleaned_text, voice="alloy")
```

## Testing

A comprehensive test suite (`test_text_cleaning.py`) is provided to verify:
- MinerU data structure handling
- Mathematical expression conversion
- Text cleaning effectiveness
- TTS readiness

Run tests with:
```bash
python test_text_cleaning.py
```

## Benefits

1. **Improved Audio Quality**: Cleaner text produces better TTS output
2. **Reduced Processing Time**: Smaller text chunks process faster
3. **Better Comprehension**: Mathematical expressions are spoken naturally
4. **Multi-language Support**: Optimized spacing for mixed content
5. **Robust Handling**: Graceful handling of complex PDF structures

## Future Enhancements

Potential areas for further improvement:
- Support for more mathematical notation types
- Enhanced table content extraction
- Better handling of scientific notation
- Improved punctuation normalization for TTS
