# System Architecture - AI Business Intelligence Agent

Comprehensive documentation of the system architecture, data flow, and component interactions.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Streamlit)                  │
│                  File Upload | Question Input                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Session State      │
                    │  - Data Agent       │
                    │  - RAG Agent        │
                    │  - Research Agent   │
                    │  - Chat History     │
                    └──────────┬──────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   SUPERVISOR AGENT                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Question Router                                           │ │
│  │  - Analyzes user question                                  │ │
│  │  - Scores relevance for each agent type                   │ │
│  │  - Determines routing path                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐  ┌───▼──────┐  ┌──▼──────────┐
        │  DATA AGENT  │  │ RAG AGENT│  │ RESEARCH   │
        │              │  │          │  │ AGENT      │
        └──────────────┘  └──────────┘  └────────────┘
                │              │              │
        ┌───────▼──────┐  ┌───▼──────┐  ┌──▼──────────┐
        │Pandas/NumPy  │  │Document  │  │ Knowledge  │
        │SQLite        │  │ Store    │  │ Base       │
        │Schema Mapper │  │Retriever │  │Explanations│
        └──────────────┘  └──────────┘  └────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Result Combiner   │
                    │ Merge agent results │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Response Formatter │
                    │  Add visualizations │
                    │  Add sources        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Display Results   │
                    │   Charts & Tables   │
                    └─────────────────────┘
```

## 📊 Component Details

### 1. User Interface Layer (Streamlit)

**File:** `app/streamlit_app.py`

**Responsibilities:**
- File upload handling
- Question input/output
- Result visualization
- Chat history management
- Example suggestions

**Flow:**
```
User Input → File Upload
           → Question Input
           → Display Results
           → Show Charts
```

### 2. Session State Management

**Maintains:**
- DataAgent instance (loaded data)
- RAGAgent instance (documents)
- ResearchAgent instance (knowledge)
- SupervisorAgent instance (orchestrator)
- Chat history

**Purpose:** Persist state across Streamlit reruns

### 3. Supervisor Agent (Orchestrator)

**File:** `agents/supervisor_agent.py`

**Components:**
- `QuestionRouter`: Routes questions to agents
- `SupervisorAgent`: Executes agents and combines results

**Routing Logic:**
```python
DATA_AGENT →
  - Revenue questions
  - Profit analysis
  - Product performance
  - Regional analysis
  - Trend analysis

RAG_AGENT →
  - Document questions
  - Policy inquiries
  - Guideline lookup

RESEARCH_AGENT →
  - Industry trends
  - General knowledge
  - Explanations
```

**Scoring Algorithm:**
- Keyword matching (data-agent keywords vs question)
- Context awareness (is data loaded?)
- Combined scoring for multiple agents

### 4. Data Agent (Business Intelligence)

**File:** `agents/data_agent.py`

**Workflow:**
```
User Question
    ↓
Intent Detection
    ↓
Schema Lookup
    ↓
Data Validation
    ↓
Pandas Calculation
    ↓
Result Formatting
    ↓
Return Answer
```

**Key Features:**
- Never hallucinates data
- Always uses actual calculations
- Intelligent column mapping
- Error handling for missing data

**Supported Queries:**
```
Total Revenue      → df['revenue_col'].sum()
Total Cost         → df['cost_col'].sum()
Total Profit       → df['revenue_col'].sum() - df['cost_col'].sum()
Profit Margin      → (profit / revenue) * 100
Average Order Value → df['revenue_col'].mean()
Top Products       → df.groupby('product')['revenue'].nlargest()
Revenue by Region  → df.groupby('region')['revenue'].sum()
Monthly Sales      → df.resample('M')['revenue'].sum()
```

### 5. Schema Mapper (Column Recognition)

**File:** `utils/schema_mapper.py`

**Purpose:** Map different column naming conventions to standard fields

**Recognition Examples:**
```
"Sales", "Revenue", "Sales_Amount" → revenue field
"Cost", "COGS", "Production_Cost" → cost field
"Qty", "Units", "Units_Sold"      → quantity field
"Date", "Order_Date", "Created_At" → date field
"Product", "Item", "SKU"           → product field
"Region", "Location", "Territory"  → region field
```

**Algorithm:**
1. Normalize column name (lowercase, remove separators)
2. Match against known aliases
3. Score confidence (1.0 = exact, 0.8 = contains, 0.6 = contained in)
4. Return best match if confidence > 0.6

### 6. Data Analyzer (Calculations)

**File:** `tools/data_tools.py`

**Class:** `DataAnalyzer`

**Methods:**
```python
get_total_revenue()           # Sum of revenue column
get_total_cost()              # Sum of cost column
get_total_profit()            # Profit calculation
get_profit_margin()           # (Profit/Revenue)*100
get_average_order_value()     # Mean of revenue
get_top_products(n=5)         # Top N products by revenue
get_revenue_by_region()       # Grouped by region
get_monthly_sales()           # Grouped by month
get_highest_revenue_product() # argmax
get_highest_revenue_region()  # argmax
```

**No Hallucination:**
- All calculations use actual data
- Clear error messages for missing data
- Returns (success, value, message) tuples

### 7. RAG Agent (Document Analysis)

**File:** `agents/rag_agent.py`

**Components:**
- `DocumentStore`: Simple document storage
- `RAGAgent`: Document search and retrieval
- `SimpleRAGPipeline`: End-to-end RAG workflow

**Workflow:**
```
Document Upload
    ↓
Document Storage
    ↓
User Question
    ↓
Keyword Search
    ↓
Retrieve Relevant Documents
    ↓
Extract Relevant Excerpts
    ↓
Return Answer + Sources
```

**Search Algorithm:**
1. Parse question into keywords
2. Search document content for matching keywords
3. Score documents by number of matches
4. Return top K documents
5. Extract relevant excerpts

**Future Enhancement:**
- Replace keyword search with embeddings
- Add vector database (FAISS, Pinecone, etc.)
- Implement semantic search

### 8. Research Agent (Knowledge)

**File:** `agents/research_agent.py`

**Features:**
- Local knowledge base for common business metrics
- Extensible for web search APIs
- Metric explanations and calculations
- Trend analysis tools

**Current Capabilities:**
```
Knowledge Base Topics:
- Profit Margin explanation
- ROI calculation
- Revenue concepts
- Market trends
- Sales performance

Future: Web Search Integration
- Serper API support
- Google Search support
- Source citations
```

### 9. Data Loader & Validation

**Files:**
- `utils/data_loader.py` - File loading
- `utils/validators.py` - Data validation

**Supported Formats:**
- CSV (comma-separated, tab-separated)
- Excel (.xlsx, .xls)
- Text (.txt)

**Validation:**
- File existence and size
- Data type checking
- Missing value detection
- Business rule validation

## 🔄 Data Flow Examples

### Example 1: "What is the total revenue?"

```
1. Streamlit UI
   ├─ User types question
   └─ Sends to supervisor

2. Supervisor Agent
   ├─ Question Router
   │  └─ Scores agents: DATA_AGENT (0.9), RAG (0.1), RESEARCH (0.1)
   ├─ Routes to DATA_AGENT
   └─ Executes DATA_AGENT

3. Data Agent
   ├─ Recognizes "revenue" intent
   ├─ Schema Mapper finds revenue column
   ├─ Calls DataAnalyzer.get_total_revenue()
   │  └─ df['Revenue'].sum() = $3,341,100
   ├─ Returns success result
   └─ Sends to Supervisor

4. Supervisor
   ├─ Combines results
   ├─ Returns: "Total revenue: $3,341,100"
   └─ Sends to UI

5. Streamlit UI
   ├─ Displays answer
   ├─ Stores in chat history
   └─ Renders to user
```

### Example 2: "Which region performed best?"

```
1. Supervisor
   ├─ Recognizes data + analysis intent
   └─ Routes to DATA_AGENT

2. Data Agent
   ├─ Intent: Revenue by region, then highest
   ├─ Calls get_revenue_by_region()
   │  └─ df.groupby('Region')['Revenue'].sum()
   ├─ Calls get_highest_revenue_region()
   │  └─ max(revenue_dict)
   ├─ Returns: {"region": "North", "revenue": $850,000}
   └─ Sends to Supervisor

3. UI
   ├─ Displays answer
   ├─ Generates bar chart
   ├─ Shows data visualization
   └─ Updates chat history
```

## 🛡️ Error Handling

### File Upload Errors

```
Invalid File
├─ File size > 10MB → "File too large"
├─ Wrong format    → "Unsupported format"
├─ Empty file      → "File is empty"
└─ Read error      → "Error loading file"

Data Issues
├─ No revenue col  → "Revenue column not found"
├─ Invalid dates   → "Invalid date format"
├─ Missing values  → "N missing values in column X"
└─ Wrong types     → "Column is not numeric"
```

### Query Errors

```
Question Processing
├─ No data loaded       → "Please upload data first"
├─ Column not found     → "Required column not found"
├─ Invalid calculation  → "Cannot calculate without revenue"
├─ Ambiguous question   → "Could not understand question"
└─ API error            → "Error processing question"
```

## 📈 Performance Considerations

### Optimization

**Data Loading:**
- Lazy loading of large datasets
- Pandas dtype optimization
- Memory-efficient groupby operations

**Caching:**
- Streamlit @st.cache_data for DataFrames
- Cached schema detection
- Reuse of calculations

**Query Optimization:**
- Vectorized Pandas operations
- Avoid loops, use groupby
- Pre-filter data before aggregation

### Scalability Limits

- Dataset size: < 1M rows (optimal)
- File size: < 10MB
- Response time: < 5 seconds typical
- Concurrent users: Depends on deployment

## 🔌 Extensibility

### Adding New Calculation

1. Add method to `DataAnalyzer` class
2. Add intent recognition to `DataAgent.process_question()`
3. Handle in Data Agent UI display

### Adding New Agent Type

1. Create new agent class in `agents/`
2. Add routing keywords to `QuestionRouter`
3. Register in `SupervisorAgent.__init__()`

### Swapping LLM Provider

```python
# In models/llm.py
LLMFactory.PROVIDERS['new_provider'] = NewProvider

# In .env
LLM_PROVIDER=new_provider
API_KEY=your-key
```

## 📊 Database Schema (Future)

```sql
-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- Datasets
CREATE TABLE datasets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(255),
    file_path VARCHAR(500),
    schema_mapping JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Queries
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    dataset_id INTEGER,
    question TEXT,
    answer TEXT,
    agent_used VARCHAR(50),
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);
```

## 🚀 Deployment Architecture

### Local Development
```
Streamlit UI (http://localhost:8501)
    ↓
Python Process (app/streamlit_app.py)
    ↓
All Agents (Memory)
    ↓
Local Data (CSV/Excel)
```

### Docker Container
```
Port 8501 (External)
    ↓
Streamlit Server (Container)
    ↓
Application Code
    ↓
Volume Mounts (Data)
```

### Cloud Deployment (Streamlit Cloud)
```
GitHub Repository
    ↓
Streamlit Cloud Build
    ↓
Deployed App (streamlit.app)
    ↓
Environment Variables (API Keys)
```

---

**Last Updated:** 2024
**Version:** 1.0
