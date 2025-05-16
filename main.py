import streamlit as st
import requests
from app.backend.evaluator import StartupEvaluator

evaluator = StartupEvaluator()
    

def frontend_app():
    st.set_page_config(
        page_title="Web Scraping AI - Avaliador de Startups",
        page_icon="🚀",
        layout="wide"
    )

    # api_status = check_api_health(api_url)
    # if not api_status:
    #     st.error("❌ API não está disponível. Verifique se o backend está rodando.")
    #     st.stop()
    # else:
    #     st.success("✅ Conectado à API")

    # Interface
    st.title("🚀 Web Scraping AI - Avaliador de Startups oficial da [AEficaz](https://aeficaz.com/)")
    st.write("Análise automatizada de startups por meio de suas páginas web usando IA")

    with st.form("evaluation_form"):
        url = st.text_input("URL da Startup:", placeholder="https://exemplo.com")
        submitted = st.form_submit_button("Avaliar")

    if submitted and url:
        with st.spinner("Analisando a startup..."):
            try:
                # if USE_API:
                #     # Abordagem com API
                #     response = requests.post(api_url, json={"url": url})
                #     if response.status_code != 200:
                #         st.error("Erro ao processar a requisição")
                #         st.stop()
                #     result = response.json()
                # else:
                #     # Abordagem Direta
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
