
### README_EN.md (английская версия)

```markdown
# 🔍 WhatsMyFinder

**OSINT Tool for Username Search Across Multiple Platforms**

[Russian Version](README.md)

## 📋 Description

WhatsMyFinder is an OSINT reconnaissance tool that allows you to search for profiles by username across hundreds of websites and social networks. The tool uses the database from the [WebBreacher/WhatsMyName](https://github.com/WebBreacher/WhatsMyName) project and provides a convenient interface for searching and analysis.

## ✨ Features

- 🔍 **Username search** on 700+ websites
- 📂 **Category selection** (social media, gaming, IT, etc.)
- 📊 **Multiple report formats**: HTML, CSV, TXT
- 🌍 **Language support**: English and Russian
- ⚙️ **Flexible settings**: timeouts, concurrent requests
- 📁 **Auto-saved reports** in the `reports/` folder
- 🎨 **Colored interface** for user-friendly experience

## 🚀 Installation

### Requirements
- Python 3.7 or higher
- Internet connection

### Installation on Termux
```bash
# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python python-pip

# Clone repository (or download files)
git clone https://github.com/your-username/whatsmyfinder.git
cd whatsmyfinder

# Install dependencies
pip install -r requirements.txt

# Download database
wget https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json

# Run
python whatsmyfinder.py
# Or via launch script
chmod +x start.sh
./start.sh