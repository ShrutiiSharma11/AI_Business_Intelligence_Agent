# AI Business Intelligence & Research Agent

A sophisticated AI-powered agent that analyzes business sales data through natural language questions. Upload CSV/Excel files and ask questions in plain English to get instant, accurate insights without hallucination.

## 🎯 Features

- **Natural Language Queries**: Ask questions in plain English
- **Accurate Calculations**: Uses Pandas/Python for reliable computations, never hallucinates numbers
- **Multi-Agent System**: Supervisor agent routes questions to specialized agents
- **Data Flexibility**: Supports datasets with different column naming conventions
- **Schema Mapping**: Intelligently maps variations like "Sales", "Revenue", "Sales_Amount" to standard fields
- **Business Calculations**: Revenue, profit, loss, margins, trends, regional analysis
- **Visualizations**: Automatic chart generation for trends and comparisons
- **Document Analysis (RAG)**: Upload and search company documents
- **Modular Architecture**: Easily swap LLM providers or add new capabilities

## 🏗️ Architecture

```
User (Streamlit UI)
    ↓
Supervisor Agent (Routing)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│                 │                 │                 │
Data Agent      RAG Agent      Research Agent
│                 │                 │
CSV/Excel        Documents       General Knowledge
Pandas/SQL       Vector DB       External Research
│                 │                 │
└─────────────────┴─────────────────┘
                 ↓
              LLM (OpenAI/Anthropic)
                 ↓
         Answer + Visualizations
```

## 📦 Tech Stack

- **Python 3.11**
- **Streamlit**: Web UI
- **Pandas & NumPy**: Data analysis
- **LangChain & LangGraph**: Agent orchestration
- **OpenAI API**: LLM (configurable)
- **Plotly**: Visualizations
- **SQLite**: Data storage
- **Pydantic**: Data validation
- **python-dotenv**: Environment management

## 📋 Project Structure

```
AI_Business_Intelligence_Agent/
├── app/
│   └── streamlit_app.py          # Main Streamlit application
├── agents/
│   ├── supervisor_agent.py       # Routes questions to agents
│   ├── data_agent.py             # Analyzes business data
│   ├── rag_agent.py              # Document search & analysis
│   └── research_agent.py         # External research
├── tools/
│   └── data_tools.py             # Business calculation tools
├── utils/
│   ├── schema_mapper.py          # Column name mapping
│   ├── data_loader.py            # File loading
│   └── validators.py             # Data validation
├── models/
│   └── llm.py                    # LLM configuration
├── prompts/
│   └── prompts.py                # Prompt templates
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── Dockerfile                    # Docker configuration
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- Conda (recommended)
- OpenAI API key

### 2. Setup Conda Environment

```bash
# Create environment
conda create -n ai_business_agent python=3.11

# Activate environment
conda activate ai_business_agent
```

### 3. Clone or Download Project

```bash
cd AI_Business_Intelligence_Agent
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 6. Run the Application

```bash
streamlit run app/streamlit_app.py
```

The application will open at `http://localhost:8501`

## 📊 Usage

### 1. Upload Data

- Click "Choose File" or drag & drop a CSV/Excel file
- Supports: CSV, XLSX, XLS files (max 10MB)

### 2. Ask Questions

Type questions in natural language:

```
"What is the total revenue?"
"Which product has the highest sales?"
"Show me monthly sales trend"
"Revenue by region"
"What is the profit margin?"
```

### 3. Get Answers

- Instant calculations from actual data
- Visual charts when applicable
- Source information and explanations

## 💡 Example Questions

```
Revenue Analysis:
- What is the total revenue?
- Total revenue by product
- Revenue by region
- Monthly revenue trend

Profit Analysis:
- How much profit did we make?
- What is the profit margin?
- Highest profit product
- Monthly profit trend

Product Analysis:
- Which product has the highest sales?
- Top 5 products
- Product performance comparison

Regional Analysis:
- Which region generated the highest revenue?
- Sales by region
- Region comparison

Other:
- What is the average order value?
- How much did we lose?
- Compare 2024 and 2025 sales
```

## 🧠 How It Works

### Data Agent

1. **Load**: Reads CSV/Excel files into Pandas DataFrame
2. **Schema Detection**: Intelligently maps column names
   - Recognizes "Sales", "Revenue", "Sales_Amount" as revenue
   - Recognizes "Cost", "COGS", "Total_Cost" as cost
   - Flexible with different naming conventions
3. **Validate**: Checks data integrity and availability
4. **Calculate**: Performs business calculations
5. **Explain**: Provides human-readable answers

### Schema Mapping

The system recognizes these field variations:

```python
Revenue: revenue, sales, sales_amount, net_sales, total_sales
Cost: cost, cogs, cost_of_goods_sold, total_cost
Profit: profit, net_profit, gross_profit
Quantity: quantity, qty, units, units_sold
Date: date, order_date, sale_date
Product: product, product_name, item
Region: region, location, state, territory
Customer: customer, customer_name, buyer
```

### Supervisor Agent

Routes questions to appropriate agents:

```
DATA_AGENT: Business data questions
  → Revenue, profit, products, regions

RAG_AGENT: Document questions
  → Policies, guidelines, procedures

RESEARCH_AGENT: General knowledge
  → Market trends, explanations
```

### Calculations

Never hallucinate - always calculate from actual data:

```python
Total Revenue = SUM(revenue_column)
Total Profit = SUM(profit_column) OR SUM(revenue - cost)
Profit Margin = (Profit / Revenue) * 100
Average Order Value = SUM(revenue) / COUNT(orders)
```

## 🔑 API Configuration

### OpenAI

```bash
# .env file
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

### Anthropic Claude (Optional)

```bash
ANTHROPIC_API_KEY=your-key-here
LLM_PROVIDER=anthropic
```

## 🔍 Dataset Examples

### Example 1: Standard E-commerce
```
Order_ID, Order_Date, Product, Category, Region, 
Quantity, Revenue, Cost, Profit, Customer
```

### Example 2: Sales Database
```
Date, Sales_Channel, Product_Name, Units_Sold, 
Sale_Amount, Production_Cost, Location
```

### Example 3: Business Report
```
Order_Date, Product_ID, Qty, Price, Total_Sales, 
COGS, Net_Profit, Territory
```

The system automatically maps these to a standard schema.

## 📈 Supported Business Metrics

| Metric | Calculation | Use Case |
|--------|-------------|----------|
| Total Revenue | SUM(revenue_col) | Overall sales |
| Total Cost | SUM(cost_col) | Expense tracking |
| Total Profit | Revenue - Cost | Bottom line |
| Profit Margin | (Profit/Revenue)*100 | Efficiency % |
| Average Order Value | Revenue / Count | Customer value |
| Top Products | GROUP BY & SUM | Performance |
| By Region | GROUP BY location | Geographic analysis |
| Monthly Trend | GROUP BY month | Time series |

## 🛡️ Error Handling

The system gracefully handles:

- ✅ Missing columns → Clear message about unavailable data
- ✅ Invalid files → Format validation and error messages
- ✅ Empty datasets → Informative error messages
- ✅ API failures → Fallback responses
- ✅ Malformed queries → Suggestions for reformulation

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t ai-business-agent .
```

### Run Container

```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key \
  ai-business-agent
```

Access at: `http://localhost:8501`

## 📝 Sample Data

A sample dataset is included in `data/sample_sales_data.xlsx` for testing.

## 🧪 Testing

### Manual Testing

1. Upload `sample_sales_data.xlsx`
2. Try example questions
3. Verify calculations match manually

### Validation Scripts

Run validation tests:

```bash
python -m pytest evaluation/
```

## 🚧 Limitations

- Web search requires external API configuration
- Vector store currently uses basic keyword matching
- Document processing limited to text extraction
- Numerical calculations only (no NLP generation)

## 🔮 Future Enhancements

- [ ] Vector database with embeddings (FAISS, Pinecone)
- [ ] Advanced NLP for complex queries
- [ ] Multi-table joins and relationships
- [ ] Real-time data streaming
- [ ] Machine learning predictions
- [ ] Export reports (PDF, Excel)
- [ ] User authentication & multi-tenancy
- [ ] Historical data versioning
- [ ] Advanced visualizations (Tableau integration)
- [ ] Mobile app support

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Create `.env` file with your key
```bash
cp .env.example .env
# Edit .env and add OPENAI_API_KEY=sk-...
```

### Issue: "File format not supported"
**Solution**: Convert to CSV or Excel (.xlsx)
- Use LibreOffice to convert formats
- Check file extension is .csv or .xlsx

### Issue: "No such module"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Chart not showing
**Solution**: Ensure Plotly is installed
```bash
pip install plotly
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review example questions
3. Check if data is properly formatted
4. Verify API key is configured

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/)

## 📊 Performance Tips

1. **Optimize Data**: Use CSV instead of Excel for large files
2. **Column Naming**: Use standard column names for faster mapping
3. **Data Size**: Keep datasets under 1M rows for fast processing
4. **Query Time**: Complex aggregations may take time on large datasets

## 🔒 Security Considerations

- Never commit `.env` file with real API keys
- Use environment variables for all secrets
- Validate all user inputs
- Run in isolated environment
- Review data before sharing results
- Use VPN/SSL for production

---

**Made with ❤️ for intelligent business analysis**
