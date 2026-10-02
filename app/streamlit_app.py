"""
AI Business Intelligence Agent - Streamlit Application
Main entry point for the application.
"""

import streamlit as st
import sys
import logging
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from utils.schema_mapper import SchemaMatcher
from agents.data_agent import DataAgent
from agents.rag_agent import RAGAgent
from agents.research_agent import ResearchAgent
from agents.supervisor_agent import SupervisorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Business Intelligence Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .file-info {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d1e7dd;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        border-left: 4px solid #198754;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "data_agent" not in st.session_state:
    st.session_state.data_agent = DataAgent()
    st.session_state.rag_agent = RAGAgent()
    st.session_state.research_agent = ResearchAgent()
    st.session_state.supervisor = SupervisorAgent(
        data_agent=st.session_state.data_agent,
        rag_agent=st.session_state.rag_agent,
        research_agent=st.session_state.research_agent
    )
    st.session_state.chat_history = []
    st.session_state.data_loaded = False


def render_header():
    """Render application header."""
    st.markdown('<div class="main-header">📊 AI Business Intelligence Agent</div>', unsafe_allow_html=True)
    st.markdown("Ask questions about your business data using natural language")
    st.divider()


def render_file_upload():
    """Render file upload section."""
    st.subheader("📁 Upload Your Data")

    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Supported formats: CSV, Excel (.xlsx, .xls)"
        )

    if uploaded_file:
        with st.spinner("Loading file..."):
            # Save uploaded file temporarily
            file_path = Path("data") / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Load file
            df, load_msg = DataLoader.load_file(file_path)

            if df is not None:
                # Clean DataFrame
                df = DataLoader.clean_dataframe(df)

                # Load into data agent
                result = st.session_state.data_agent.load_data(df)

                if result["success"]:
                    st.session_state.data_loaded = True
                    st.success(f"✅ {load_msg}")

                    # Show data info
                    with st.expander("📋 Data Information"):
                        summary = result["summary"]
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Rows", summary["rows"])
                        with col2:
                            st.metric("Columns", summary["columns"])
                        with col3:
                            st.metric(
                                "Memory",
                                f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
                             )
                        st.write("**Columns:**")
                        st.write(", ".join(summary["column_names"]))

                        st.write("**Schema Mapping:**")
                        schema = result["schema_mapping"]
                        for col, field_type in schema.items():
                            st.write(f"- {col} → {field_type}")

                else:
                    st.error(f"Failed to load data: {result.get('error')}")
            else:
                st.error(f"❌ {load_msg}")


def render_chat_interface():
    """Render chat interface."""
    st.subheader("💬 Ask Questions About Your Data")

    if not st.session_state.data_loaded:
        st.info("👆 Please upload a file first to ask questions")
        return

    # Chat history
    if st.session_state.chat_history:
        with st.expander("📝 Chat History", expanded=False):
            for i, msg in enumerate(st.session_state.chat_history):
                st.write(f"**Q{i+1}:** {msg['question']}")
                st.write(f"**A:** {msg['answer']}")
                st.divider()

    # Question input
    col1, col2 = st.columns([4, 1])

    with col1:
        question = st.text_input(
            "Your question:",
            placeholder="e.g., What is the total revenue? Which product has the highest sales?",
            key="question_input"
        )

    with col2:
        send_button = st.button("🔍 Ask", use_container_width=True)

    # Process question
    if send_button and question:
        with st.spinner("Analyzing..."):
            try:
                # Get routing decision
                result = st.session_state.supervisor.process_question(question)

                # Extract answer
                combined_answer = result.get("combined_answer", "No answer generated")

                # Display answer
                st.markdown("### Answer")
                st.write(combined_answer)

                # Display data from data agent if available
                if "DATA_AGENT" in result.get("agent_results", {}):
                    data_result = result["agent_results"]["DATA_AGENT"]
                    if data_result.get("success"):
                        # Check if chart data is available
                        if data_result.get("type") in ["monthly_sales", "revenue_by_region", "top_products"]:
                            render_chart(data_result)

                # Store in history
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": combined_answer
                })

                st.divider()

            except Exception as e:
                st.error(f"Error processing question: {str(e)}")
                logger.error(f"Error: {str(e)}")


def render_chart(result: dict):
    """Render visualization if applicable."""
    try:
        import plotly.graph_objects as go
        import plotly.express as px

        result_type = result.get("type")
        data = result.get("data", {})

        if result_type == "monthly_sales" and data:
            st.markdown("### 📈 Monthly Sales Trend")
            months = list(data.keys())
            values = list(data.values())

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months, y=values,
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))

            fig.update_layout(
                title="Monthly Sales Trend",
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        elif result_type == "revenue_by_region" and data:
            st.markdown("### 📊 Revenue by Region")
            regions = list(data.keys())
            values = list(data.values())

            fig = go.Figure(data=[
                go.Bar(x=regions, y=values, marker_color='#1f77b4')
            ])

            fig.update_layout(
                title="Revenue by Region",
                xaxis_title="Region",
                yaxis_title="Revenue ($)",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        elif result_type == "top_products" and data:
            st.markdown("### 🏆 Top Products")
            products = [item["product"] for item in data]
            revenues = [item["revenue"] for item in data]

            fig = go.Figure(data=[
                go.Bar(y=products, x=revenues, orientation='h', marker_color='#1f77b4')
            ])

            fig.update_layout(
                title="Top Products by Revenue",
                xaxis_title="Revenue ($)",
                yaxis_title="Product",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        logger.error(f"Chart rendering error: {str(e)}")


def render_examples():
    """Render example questions."""
    with st.expander("💡 Example Questions", expanded=False):
        examples = [
            "What is the total revenue?",
            "Which product has the highest sales?",
            "What is the profit margin?",
            "Show me monthly sales trend",
            "Revenue by region",
            "Top 5 products",
            "What is the average order value?",
            "How much profit did we make?",
            "Which region generated the highest revenue?",
            "What is our total cost?"
        ]

        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(example, key=f"example_{i}", use_container_width=True):
                    st.session_state.question_input = example
                    st.rerun()


def main():
    """Main application."""
    render_header()

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        if st.session_state.data_loaded:
            st.success("✅ Data Loaded")

            if st.button("🔄 Clear Data", use_container_width=True):
                st.session_state.data_loaded = False
                st.session_state.data_agent = DataAgent()
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.write("""
        **AI Business Intelligence Agent** helps you analyze business data through natural language questions.

        **Features:**
        - Upload CSV/Excel files
        - Ask questions in natural language
        - Get accurate calculations (no hallucination)
        - View trends and insights
        - Export results
        """)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        render_file_upload()
        render_chat_interface()

    with col2:
        render_examples()

        st.markdown("---")
        st.markdown("### 📊 Supported Metrics")
        st.write("""
        - Total Revenue
        - Total Cost
        - Total Profit
        - Profit Margin
        - Average Order Value
        - Top Products
        - Revenue by Region
        - Monthly Trends
        """)


if __name__ == "__main__":
    main()
