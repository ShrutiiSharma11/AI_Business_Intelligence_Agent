# Setup Guide - AI Business Intelligence Agent

This guide walks you through setting up the AI Business Intelligence Agent on your local machine.

## 📋 Prerequisites

Before you start, make sure you have:

- **Windows 10+, macOS 10.13+, or Linux**
- **Python 3.11** (or higher)
- **Conda** (optional but recommended)
- **Git** (optional)
- **OpenAI API Key** (required for LLM functionality)

### Check Python Version

```bash
python --version
# or
python3 --version
```

Should show Python 3.11 or higher.

## 🚀 Step-by-Step Setup

### Step 1: Install Conda (Optional but Recommended)

#### Windows
Download from: https://www.anaconda.com/download
Run installer and follow prompts.

#### macOS
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

#### Linux
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### Step 2: Download Project

#### Option A: Using Git
```bash
git clone <repository-url>
cd AI_Business_Intelligence_Agent
```

#### Option B: Manual Download
1. Download the project folder
2. Extract to desired location
3. Open terminal/command prompt in project folder

### Step 3: Create Python Environment

#### Using Conda (Recommended)
```bash
# Create environment with Python 3.11
conda create -n ai_business_agent python=3.11

# Activate environment
conda activate ai_business_agent

# Verify
python --version  # Should show 3.11.x
```

#### Using venv (Alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify
python --version  # Should show 3.11.x
```

### Step 4: Install Dependencies

Make sure your environment is activated, then run:

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep streamlit
# Should show streamlit version
```

### Step 5: Configure Environment Variables

#### Create .env file

```bash
# Copy the example file
cp .env.example .env

# Edit .env (use your favorite editor)
# Windows: notepad .env
# macOS/Linux: nano .env
```

#### Edit .env file

Open `.env` and add your OpenAI API key:

```env
# API Configuration
OPENAI_API_KEY=sk-your-actual-key-here

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800
```

**Where to get OpenAI API Key:**

1. Go to: https://platform.openai.com/api-keys
2. Log in (create account if needed)
3. Click "Create new secret key"
4. Copy the key
5. Paste in .env file

**⚠️ IMPORTANT: Never commit .env file to Git**

### Step 6: Verify Installation

Run the validation tests:

```bash
python evaluation/test_calculations.py
```

Should see: ✅ PASS for all tests

### Step 7: Run the Application

```bash
# Make sure you're in the project directory
# And your Conda environment is activated

streamlit run app/streamlit_app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser and go to: **http://localhost:8501**

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Project folder downloaded
- [ ] Conda environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with OpenAI API key
- [ ] Validation tests pass
- [ ] Streamlit app runs on http://localhost:8501
- [ ] Can upload CSV file
- [ ] Can ask questions about data

## 🎯 First Time Usage

1. **Start the app**
   ```bash
   streamlit run app/streamlit_app.py
   ```

2. **Open in browser**
   Go to http://localhost:8501

3. **Upload sample data**
   Click "Choose File" and select `data/sample_sales_data.csv`

4. **Ask a question**
   Type: "What is the total revenue?"

5. **See the answer**
   Application should calculate and display the result

## 🐛 Troubleshooting

### "Python 3.11 not found"
**Solution:** Install Python 3.11 from https://www.python.org/downloads/

```bash
# Check Python version
python --version
python3 --version

# You might need to use python3 instead of python
python3 -m venv venv
```

### "OPENAI_API_KEY not found"
**Solution:** 
1. Create .env file: `cp .env.example .env`
2. Add your API key to .env
3. Restart the application

### "ModuleNotFoundError: No module named 'streamlit'"
**Solution:** Make sure your environment is activated and dependencies are installed
```bash
# Activate environment
conda activate ai_business_agent  # or: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8501 already in use"
**Solution:** Streamlit is running on a different port
```bash
streamlit run app/streamlit_app.py --server.port 8502
```

### "File not found" error
**Solution:** Make sure you're in the correct directory
```bash
# Should be in project root directory
pwd  # or: cd to project directory
ls -la  # Should see requirements.txt, README.md, etc.
```

### File upload fails
**Solution:**
1. Check file format (must be CSV or Excel)
2. Check file size (max 10MB)
3. Check file contains headers in first row
4. Try uploading sample data first

## 📊 Testing with Sample Data

Sample data is provided in `data/sample_sales_data.csv`

**Content:**
- 2,757 transactions
- Order dates from 2024-01-01 to 2024-12-31
- 5 regions: North, South, East, West, Central
- 5 products: Product A-E
- Revenue, Cost, and Profit columns

**Try these questions:**
1. "What is the total revenue?"  → Expected: $3,341,100
2. "What is the total profit?"   → Expected: $2,004,660
3. "Which product has highest sales?"
4. "Show monthly sales trend"
5. "Revenue by region"

## 🔄 Updating Dependencies

If you need to update packages:

```bash
# Activate your environment
conda activate ai_business_agent

# Update pip
pip install --upgrade pip

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

## 🐳 Docker Setup (Alternative)

### Build Docker Image
```bash
docker build -t ai-business-agent .
```

### Run Docker Container
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key-here \
  ai-business-agent
```

Access at: http://localhost:8501

## 📱 VS Code Setup

### Open Project in VS Code

1. Open VS Code
2. File → Open Folder
3. Select the project folder
4. Click "Open"

### Select Python Interpreter

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type: "Python: Select Interpreter"
3. Choose the one with "ai_business_agent" environment

### Run from VS Code

1. Open Terminal in VS Code (Ctrl+`)
2. Run: `streamlit run app/streamlit_app.py`

## 🚀 Running in Production

### Cloud Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy from your GitHub repository

### Cloud Deployment (AWS/GCP/Azure)

See README.md for Docker and cloud platform instructions.

## 📞 Getting Help

1. Check the README.md file
2. Review example questions in the app
3. Check troubleshooting section
4. Verify .env file configuration
5. Check logs in console

## ✨ Next Steps

After setup:

1. Explore with sample data
2. Upload your own CSV file
3. Try different questions
4. Check visualizations
5. Review agent routing decisions
6. Explore code structure

Happy analyzing! 📊
