import streamlit as st
import requests
from app.backend.evaluator import StartupEvaluator

# Configuração da página
st.set_page_config(
    page_title="Web Scraping AI - Avaliador de Startups",
    page_icon="🚀",
    layout="wide"
)

# Configurações
USE_API = False  # Mude para True para usar a abordagem com API

if USE_API:
    API_URL = "http://localhost:8000/evaluate"
else:
    evaluator = StartupEvaluator()

# Interface
st.title("🚀 Web Scraping AI - Avaliador de Startups")
st.write("Análise automatizada de startups por meio de suas páginas web usando IA")

with st.form("evaluation_form"):
    url = st.text_input("URL da Startup:", placeholder="https://exemplo.com")
    submitted = st.form_submit_button("Avaliar")

if submitted and url:
    with st.spinner("Analisando a startup..."):
        try:
            if USE_API:
                # Abordagem com API
                response = requests.post(API_URL, json={"url": url})
                if response.status_code != 200:
                    st.error("Erro ao processar a requisição")
                    st.stop()
                result = response.json()
            else:
                # Abordagem Direta
                result = evaluator.evaluate(url)

            # Exibição dos resultados
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 Descrição")
                st.write(result["descriptor"])
                
                st.subheader("💡 Insights")
                for thought in result["thoughts"]:
                    st.write(f"• {thought}")
                
                st.subheader("📊 Tendências de Mercado")
                st.write(result["market_trends"])
            
            with col2:
                st.subheader("⭐ Avaliação Final")
                st.metric("Nota", result["rating"], "de 10")
                st.write(result["final_answer"])

        except Exception as e:
            st.error(f"Erro ao processar a avaliação: {str(e)}")
            st.exception(e)  # Isso mostrará o traceback completo

# Footer
st.markdown("---")
st.markdown("### Sugestões de startups para teste:")
st.markdown("""
1. https://brintell.com.br/            
2. https://www.cleverdash.ai/
3. https://ia.adapta.org/
4. https://lovable.dev/
5. https://devin.ai/
6. https://manus.im/
""")