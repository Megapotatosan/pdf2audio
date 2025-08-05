#!/usr/bin/env python3
"""
Test script to demonstrate the improved text cleaning for MinerU data
"""

import json
from pdf_to_audio import PDFToAudioConverter

def test_mineru_text_cleaning():
    """Test the MinerU text cleaning with sample data"""
    
    # Sample data structure like the one you provided
    sample_data = {
        'backend': 'pipeline',
        'version': '2.1.7',
        'results': {
            '01. 通告- 員工意見箱 1 Nov 2020': {
                'md_content': '''# 通告

日期 2020年11月1日致 全體員工

# 優化員工内部溝通渠道

為加强公司與員工之間的溝通渠道，增進與員工之間的緊密關係與凝聚力，人力資源及行政部現安排（1）意見箱 及(2）電郵 讓大家透過這平台能給予寶貴意見。

歡迎各員工就公司環境、福利及政策等給予任何意見，讓公司更能從中瞭解在各方面仍有成長空間，目標做到「追求進步」！

意見箱分別設於8樓及9樓影印機附近位置(請參看下圖相片)及各地盤寫字樓:

![](images/4e50d4954edc4e0c3100726c43e0c4bb8fc932bddcb1f047cd2a1baa109702a1.jpg)

除意見箱外，員工亦可透過電郵給予意見。電郵地址是kwopinion@kinwing.com.hk

所有意見由高級人力資源及行政部經理於每星期收集一次，全部均由以下職位檢閱:

董事及總經理及高級人力資源及行政部經理

此渠道皆適用於建業建榮控股有限公司之附屬公司。

此致

![](images/7b56f609e5631346e32893b643e7a04d342c216e9b4b641ba2e822a35e578a1c.jpg)

蘇顯光董事及總經理

# Memorandum

Date 1November2020 To All staff members

# Re: Optimization of Internal Staff Communication Channel

In order to strengthen the communication channel between the Company and all staff members,and enhance close relationship and cohesion, the Human Resources Department arrange (1) the opinion boxes and (2) email to collect your valuable opinion(s) through this platform.

All staff members are welcome to give any opinion about the workplace environment, staff benefit and company policies,so that the Company can better understand there is still room for growth in all aspects,we aim to be better!

The Opinion Boxes are located at $8 ^ { \\mathrm { t h } }$ floor and $9 ^ { \\mathrm { t h } }$ floor near the copying area and each site office. Please see the following pictures for your illustration in office:

![](images/f75961872154b15ead4f7d660b9a413ceea7948880cb27216d9325d8068b59b7.jpg)

Other than the Opinion Boxes,all staff members are also welcome to give your opinions via email. The email address is kwopinion@kinwing.com.hk

All opinions are collected by Senior HR & Administration Manager once a week and it must be read through and reviewed by the following positions:

Director & General Manager and Senior HR& Administration Manager

This channel shall be applicable to any subsidiary companies of "Chinney Kin Wing Holdings Limited".

Yours truly,

![](images/54c1e00933c69a26af2f163a013d452b53954f0bb974126824a9402788792dee.jpg)

H.K. So Director& General Manager

HKS/swl'''
            }
        }
    }
    
    print("🧪 Testing MinerU Text Cleaning")
    print("=" * 60)
    
    # Initialize converter
    converter = PDFToAudioConverter()
    
    # Test the extraction and cleaning
    print("📥 Processing sample MinerU data...")
    cleaned_text = converter.extract_text_from_mineru_response(sample_data)
    
    print(f"\n📊 Results:")
    print(f"Original length: {len(sample_data['results']['01. 通告- 員工意見箱 1 Nov 2020']['md_content'])} characters")
    print(f"Cleaned length: {len(cleaned_text)} characters")
    print(f"Reduction: {((len(sample_data['results']['01. 通告- 員工意見箱 1 Nov 2020']['md_content']) - len(cleaned_text)) / len(sample_data['results']['01. 通告- 員工意見箱 1 Nov 2020']['md_content']) * 100):.1f}%")
    
    print(f"\n📝 Cleaned Text Preview (first 500 characters):")
    print("-" * 50)
    print(cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text)
    print("-" * 50)
    
    # Test specific cleaning features
    print(f"\n🔍 Cleaning Features Tested:")
    original = sample_data['results']['01. 通告- 員工意見箱 1 Nov 2020']['md_content']
    
    # Check if images were removed
    images_removed = "![" not in cleaned_text
    print(f"✅ Images removed: {images_removed}")
    
    # Check if math expressions were converted
    math_converted = "$8 ^ { \\mathrm { t h } }$" not in cleaned_text and "8th" in cleaned_text
    print(f"✅ Math expressions converted: {math_converted}")
    
    # Check if email addresses were removed
    email_removed = "kwopinion@kinwing.com.hk" not in cleaned_text
    print(f"✅ Email addresses removed: {email_removed}")
    
    # Check if headers were removed
    headers_removed = "# 通告" not in cleaned_text and "# Memorandum" not in cleaned_text
    print(f"✅ Markdown headers removed: {headers_removed}")
    
    # Check Chinese-English spacing
    has_proper_spacing = " 8th " in cleaned_text or "8th floor" in cleaned_text
    print(f"✅ Proper spacing added: {has_proper_spacing}")
    
    print(f"\n🎯 Text is ready for TTS conversion!")
    
    return cleaned_text

def test_math_conversion():
    """Test mathematical expression conversion"""
    print("\n🧮 Testing Mathematical Expression Conversion")
    print("=" * 60)
    
    converter = PDFToAudioConverter()
    
    test_cases = [
        "$8 ^ { \\mathrm { t h } }$",
        "$9 ^ { \\mathrm { t h } }$", 
        "$x^2$",
        "$\\frac{1}{2}$",
        "$a ^ { \\mathrm { s t } }$"
    ]
    
    for test_case in test_cases:
        # Extract the math part (remove $ signs)
        math_part = test_case.strip('$')
        converted = converter.convert_math_to_text(math_part)
        print(f"'{test_case}' → '{converted}'")

if __name__ == "__main__":
    print("🚀 MinerU Text Cleaning Test Suite")
    print("=" * 60)
    
    # Test main cleaning functionality
    cleaned_text = test_mineru_text_cleaning()
    
    # Test math conversion specifically
    test_math_conversion()
    
    print(f"\n✨ All tests completed!")
    print(f"📄 The cleaned text is now optimized for text-to-speech conversion.")
    print(f"🎵 You can use this with OpenAI TTS for high-quality audio generation.")
