# 🚀 Quick Start - AI Business Intelligence Agent

Get up and running in 5 minutes!

## ⚡ 5-Minute Setup

### 1. Create Python Environment (1 min)

```bash
# Windows/Mac/Linux
conda create -n ai_business_agent python=3.11
conda activate ai_business_agent
```

### 2. Install Dependencies (1 min)

```bash
cd AI_Business_Intelligence_Agent
pip install -r requirements.txt
```

### 3. Setup API Key (1 min)

```bash
# Copy example
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

Get your key: https://platform.openai.com/api-keys

### 4. Run Tests (1 min)

```bash
python evaluation/test_calculations.py
```

Should see: ✅ All tests passed!

### 5. Start Application (1 min)

```bash
streamlit run app/streamlit_app.py
```

Open browser: **http://localhost:8501**

## ✅ You're Done!

### Try These:

1. **Upload Data**
   - Click "Choose File"
   - Select `data/sample_sales_data.csv`
   - Wait for "Data Loaded" message

2. **Ask Questions**
   - "What is the total revenue?"
   - "Which product has highest sales?"
   - "Show monthly sales trend"

3. **See Results**
   - Get instant answers
   - View visualizations
   - Check chat history

## 📁 Project Files

```
AI_Business_Intelligence_Agent/
├── app/
│   └── streamlit_app.py              # 🖥️ Main UI
├── agents/
│   ├── data_agent.py                 # 📊 Data analysis
│   ├── rag_agent.py                  # 📄 Document search
│   ├── research_agent.py             # 🔍 Knowledge
│   └── supervisor_agent.py           # 🎛️ Routing
├── tools/
│   └── data_tools.py                 # 🔧 Calculations
├── utils/
│   ├── schema_mapper.py              # 🗺️ Column mapping
│   ├── data_loader.py                # 📥 File loading
│   └── validators.py                 # ✔️ Data validation
├── models/
│   └── llm.py                        # 🤖 LLM config
├── prompts/
│   └── prompts.py                    # 📝 Prompt templates
├── evaluation/
│   └── test_calculations.py          # 🧪 Tests
├── data/
│   └── sample_sales_data.csv         # 📊 Sample data
├── .env.example                       # ⚙️ Config template
├── requirements.txt                   # 📦 Dependencies
├── README.md                          # 📖 Full docs
├── SETUP_GUIDE.md                     # 🛠️ Detailed setup
├── ARCHITECTURE.md                    # 🏗️ System design
└── Dockerfile                         # 🐳 Docker config
```

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `streamlit_app.py` | User interface - upload files, ask questions |
| `data_agent.py` | Analyzes business data, calculates metrics |
| `supervisor_agent.py` | Routes questions to right agent |
| `schema_mapper.py` | Recognizes different column names |
| `data_tools.py` | Business calculation functions |
| `test_calculations.py` | Validates calculations are correct |

## 💡 10 Example Questions

1. ✅ **"What is the total revenue?"**
   - Calculates sum of revenue column

2. ✅ **"How much profit did we make?"**
   - Calculates profit = revenue - cost

3. ✅ **"Which product has the highest sales?"**
   - Finds top product by revenue

4. ✅ **"What is the profit margin?"**
   - Calculates (profit/revenue)*100

5. ✅ **"Show me monthly sales trend"**
   - Groups sales by month, shows chart

6. ✅ **"Revenue by region"**
   - Breaks down revenue by location

7. ✅ **"Top 5 products"**
   - Lists top 5 products by revenue

8. ✅ **"What is the average order value?"**
   - Calculates mean transaction value

9. ✅ **"How much loss did we have?"**
   - Shows negative profit if any

10. ✅ **"Which region performed best?"**
    - Finds highest revenue region

## 🚨 Troubleshooting

### ❌ "OPENAI_API_KEY not found"
→ Create `.env` file and add your key

### ❌ "Port 8501 already in use"
→ Run on different port: `streamlit run app/streamlit_app.py --server.port 8502`

### ❌ "ModuleNotFoundError"
→ Install dependencies: `pip install -r requirements.txt`

### ❌ "Python 3.11 not found"
→ Install from https://www.python.org/downloads/

See **SETUP_GUIDE.md** for more help.

## 📊 How It Works

```
You ask: "What is total revenue?"
    ↓
Supervisor routes to Data Agent
    ↓
Data Agent finds revenue column
    ↓
Python calculates: SUM(revenue)
    ↓
Returns: "Total revenue: $3,341,100"
    ↓
Display in Streamlit UI
```

## 🎓 Key Features

✅ **No Hallucination** - All numbers come from your actual data
✅ **Smart Column Mapping** - Recognizes "Sales", "Revenue", "Sales_Amount"
✅ **Flexible Datasets** - Works with different data formats
✅ **Visual Results** - Automatic charts and visualizations
✅ **Error Handling** - Clear messages for missing data
✅ **Production Code** - Full enterprise-grade implementation

## 📖 Documentation

- **README.md** - Complete feature documentation
- **SETUP_GUIDE.md** - Detailed installation steps
- **ARCHITECTURE.md** - System design & data flow
- **This file** - Quick start guide

## 🐳 Docker (Alternative)

```bash
# Build
docker build -t ai-business-agent .

# Run
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key \
  ai-business-agent

# Open http://localhost:8501
```

## 🚀 Next Steps

1. ✅ Complete setup above
2. 📊 Upload sample data
3 💬 Ask 10 example questions
4. 📁 Upload your own CSV file
5. 🔍 Explore data insights
6. 📈 Share results

## 💬 Example Conversation

```
You:  "What is the total revenue?"
Bot:  "Total revenue: $3,341,100"

You:  "Which product had highest sales?"
Bot:  "Product E: $850,000"

You:  "Show monthly trend"
Bot:  [Shows line chart of monthly sales]

You:  "Revenue by region?"
Bot:  [Shows bar chart by region]
```

## 🔄 Common Workflow

1. **Start App**
   ```bash
   streamlit run app/streamlit_app.py
   ```

2. **Upload File**
   - Click "Choose File"
   - Select CSV or Excel

3. **Ask Questions**
   - Type in chat box
   - Get instant answers

4. **View Results**
   - See calculations
   - Check visualizations
   - Review sources

5. **Export/Share**
   - Copy answers
   - Save screenshots
   - Share insights

## ✨ That's It!

You now have a fully functional AI Business Intelligence Agent.

**Enjoy analyzing your data! 📊**

---

Need help? See **SETUP_GUIDE.md** for detailed troubleshooting.
