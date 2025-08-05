import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up PDF to Audio Converter...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo run the application:")
    print("python pdf_to_audio.py")
    print("\nThe application will be available at: http://127.0.0.1:7860")

if __name__ == "__main__":
    main()
