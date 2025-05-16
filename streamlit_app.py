import streamlit as st
import os
from app.backend.evaluator import StartupEvaluator
from dotenv import load_dotenv

# Carrega variáveis de ambiente para a API GROQ
load_dotenv()

# Inicializa o avaliador com a API key do GROQ carregada das variáveis de ambiente
evaluator = StartupEvaluator(
    model="meta-llama/llama-4-scout-17b-16e-instruct",  # Você pode ajustar o modelo conforme necessário
    temperature=0.7
)

def frontend_app():
    st.set_page_config(
        page_title="Web Scraping AI - Avaliador de Startups",
        page_icon="🚀",
        layout="wide"
    )

    # Interface
    st.title("🚀 Web Scraping AI - Avaliador de Startups oficial da [AEficaz](https://aeficaz.com/)")
    st.write("Análise automatizada de startups por meio de suas páginas web usando IA")

    with st.form("evaluation_form"):
        url = st.text_input("URL da Startup:", placeholder="https://exemplo.com")
        submitted = st.form_submit_button("Avaliar")

    if submitted and url:
        with st.spinner("Analisando a startup..."):
            try:
                # Usa o avaliador diretamente
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
    1. https://www.gupshup.io/pt/
    2. https://www.cleverdash.ai/
    3. https://ia.adapta.org/
    4. https://lovable.dev/
    5. https://devin.ai/
    6. https://manus.im/
    7. https://www.nomadglobal.com/
    """)

if __name__ == "__main__":
    frontend_app() 