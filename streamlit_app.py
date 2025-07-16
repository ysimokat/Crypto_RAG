import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from argumentrx import ArgumentRx
import json
import time

st.set_page_config(
    page_title="ArgumentRx - RAG Argumentation System",
    page_icon="🧠",
    layout="wide"
)

def init_session_state():
    if 'argumentrx' not in st.session_state:
        st.session_state.argumentrx = None
    if 'results' not in st.session_state:
        st.session_state.results = None

def main():
    init_session_state()
    
    st.title("🧠 ArgumentRx")
    st.subheader("Retrieval-Augmented Argumentation System for Real-Time Reasoning")
    
    st.markdown("""
    Generate fact-based, pro/con arguments on controversial topics using real-time evidence 
    from news sources, Reddit, and crypto research blogs.
    """)
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        use_openai = st.checkbox("Use OpenAI GPT", value=True, help="Uncheck to use local LLM")
        
        st.info("💡 Make sure to set your API keys in .env file for full functionality")
        
        with st.expander("API Keys Status"):
            from config import Config
            st.write("OpenAI:", "✅" if Config.OPENAI_API_KEY else "❌")
            st.write("Reddit:", "✅" if Config.REDDIT_CLIENT_ID else "❌") 
            st.write("News API:", "✅" if Config.NEWS_API_KEY else "❌")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "🎯 Enter a topic for argument generation:",
            placeholder="e.g., Bitcoin regulation, DeFi vs traditional banking, NFT value proposition"
        )
    
    with col2:
        generate_button = st.button("🚀 Generate Arguments", type="primary")
    
    if generate_button and topic:
        if st.session_state.argumentrx is None:
            with st.spinner("Initializing ArgumentRx..."):
                st.session_state.argumentrx = ArgumentRx(use_openai=use_openai)
        
        with st.spinner(f"Generating arguments for: {topic}"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Retrieving sources...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("🧮 Processing embeddings...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("✍️ Generating arguments...")
            progress_bar.progress(75)
            
            results = st.session_state.argumentrx.generate_arguments(topic)
            st.session_state.results = results
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            time.sleep(0.5)
            
            progress_bar.empty()
            status_text.empty()
    
    if st.session_state.results:
        results = st.session_state.results
        
        if 'error' in results:
            st.error(f"❌ {results['error']}")
            return
        
        st.success(f"✅ Generated arguments for: **{results['topic']}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 PRO Argument")
            pro_eval = results['arguments']['pro']['evaluation']
            
            col1_1, col1_2, col1_3, col1_4 = st.columns(4)
            col1_1.metric("Overall", f"{pro_eval['overall_score']}")
            col1_2.metric("Clarity", f"{pro_eval['clarity']}")
            col1_3.metric("Logic", f"{pro_eval['logic']}")
            col1_4.metric("Evidence", f"{pro_eval['evidence']}")
            
            st.write(results['arguments']['pro']['content'])
            
            with st.expander("📚 Pro Citations"):
                for citation in results['arguments']['pro']['citations']:
                    st.write(f"• {citation}")
            
            with st.expander("💬 Pro Feedback"):
                st.write(pro_eval['feedback'])
        
        with col2:
            st.subheader("📉 CON Argument")
            con_eval = results['arguments']['con']['evaluation']
            
            col2_1, col2_2, col2_3, col2_4 = st.columns(4)
            col2_1.metric("Overall", f"{con_eval['overall_score']}")
            col2_2.metric("Clarity", f"{con_eval['clarity']}")
            col2_3.metric("Logic", f"{con_eval['logic']}")
            col2_4.metric("Evidence", f"{con_eval['evidence']}")
            
            st.write(results['arguments']['con']['content'])
            
            with st.expander("📚 Con Citations"):
                for citation in results['arguments']['con']['citations']:
                    st.write(f"• {citation}")
            
            with st.expander("💬 Con Feedback"):
                st.write(con_eval['feedback'])
        
        st.subheader("📊 Source Analysis")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sources Retrieved", results['metadata']['total_sources_retrieved'])
        col2.metric("Sources Used", results['metadata']['sources_used'])
        col3.metric("Model Used", results['metadata']['model_used'])
        
        with st.expander("🔍 View All Sources"):
            for source in results['sources']:
                with st.container():
                    st.write(f"**{source['id']}. {source['title']}**")
                    st.write(f"Type: {source['type']} | Relevance: {source['relevance_score']}")
                    st.write(f"Preview: {source['preview']}")
                    st.write(f"[🔗 View Source]({source['url']})")
                    st.divider()
        
        st.subheader("📋 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Download JSON"):
                json_str = json.dumps(results, indent=2)
                st.download_button(
                    label="📥 Download Results",
                    data=json_str,
                    file_name=f"{results['topic'].replace(' ', '_')}_results.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📄 Generate Report"):
                report = st.session_state.argumentrx.get_source_transparency_report(results)
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name=f"{results['topic'].replace(' ', '_')}_transparency.md",
                    mime="text/markdown"
                )
        
        with col3:
            if st.button("🔄 Clear Results"):
                st.session_state.results = None
                st.rerun()

if __name__ == "__main__":
    main()