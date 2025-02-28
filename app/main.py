import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import time

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    # App header and description
    st.set_page_config(layout="centered", page_title="Job Application AI Agent", page_icon="📧")
    
    # Title and description section
    st.title("📧 Job Application Email AI Agent")
    st.markdown("""
    ### Turn job listings into tailored application emails based on my portfolio
    
    This tool analyzes job descriptions and automatically generates personalized application emails 
    that highlight my relevant skills and experience. It uses **ChromaDB** for semantic search of my portfolio 
    and **LangChain** to orchestrate the AI workflow. Simply paste a job listing URL below, and 
    let AI craft a customized email that showcases my specific qualifications!
    
    **How it works:**
    1. Enter the URL of a job posting
    2. LangChain extracts key skills and requirements from the listing
    3. ChromaDB performs vector similarity search to find relevant examples from my portfolio
    4. LangChain generates a customized email highlighting my matched experience
    """)
    
    # Technical details
    with st.expander("Technical Details"):
        st.markdown("""
        - **Vector Database**: ChromaDB stores embeddings of my portfolio projects and experience
        - **Orchestration**: LangChain connects the web scraper, AI model, and vector database
        - **Semantic Matching**: Uses vector similarity to find the most relevant portfolio examples
        - **Dynamic Generation**: Creates context-aware emails based on the specific job requirements
        """)
    

    url_input = st.text_input(
        "Enter job listing URL:",
        value="https://careers.kpmg.com.sg/job/ASPAC-Tax-Technology-and-Transformation-Manager/32443044/",
        placeholder="https://example.com/job-listing"
    )
    
    submit_button = st.button("Generate Email", type="primary", use_container_width=False)
    
    # Divider for visual separation
    st.divider()
    
    if submit_button:
        try:
            # Show processing status
            with st.status("Processing your request...", expanded=True) as status:
                st.write("🔍 Loading job description from URL...")
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                
                st.write("📋 Analyzing job requirements with LangChain...")
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)
                
                st.write("🧩 Querying ChromaDB for portfolio matches...")
                
                # Process each job found
                for i, job in enumerate(jobs):
                    skills = job.get('skills', [])
                    portfolio = portfolio.query_links(skills)
                    
                    st.write("✍️ Using LangChain to craft personalized email...")
                    email = llm.write_email(job, portfolio)
                    
                    # Short pause for visual effect
                    time.sleep(0.5)
                
                status.update(label="✅ Email generated successfully!", state="complete")
            
            # Display results in a nice container
            st.subheader("📤 My Personalized Application Email")
            
            # Show the job title if available
            if jobs and 'title' in jobs[0]:
                st.caption(f"For: {jobs[0]['title']}")
            
            # Email display
            with st.container():
                st.markdown("### Email Preview")
                st.markdown(email)
                
                # Add buttons for actions
        
        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
            st.info("Please check the URL and try again, or contact support if the problem persists.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)