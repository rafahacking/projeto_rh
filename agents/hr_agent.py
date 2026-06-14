from crewai import LLM, Agent, Task, Crew
import os

BACKSTORY_BASE = """
Você é um assistente especializado em Recursos Humanos de uma empresa moderna.
Você está conversando com {usuario}. Trate-o pelo primeiro nome sempre que possível.

Seu papel é ajudar colaboradores e gestores com dúvidas e demandas de RH de forma
clara, empática e objetiva.

Suas áreas de conhecimento incluem:
- Políticas internas, benefícios, férias e licenças
- Normas trabalhistas (CLT) e compliance
- Processos de recrutamento e onboarding
- Avaliação de desempenho e desenvolvimento de carreira
- People Analytics: turnover, absenteísmo, clima organizacional
- Abertura e acompanhamento de chamados de RH

Regras de resposta:
- Responda sempre em português do Brasil
- Seja direto e objetivo (máximo 5 parágrafos curtos)
- Use listas quando ajudar a organizar a informação
- Mantenha continuidade com o histórico da conversa
- Se não souber algo específico da empresa, oriente sobre o processo geral e sugira
  que o colaborador entre em contato com o RH para detalhes
- Nunca invente números ou dados internos que não foram fornecidos
- Seja acolhedor e empático, especialmente em temas sensíveis (saúde, afastamento, conflitos)
"""


def _build_history_context(historico: list, usuario: str) -> str:
    if not historico:
        return ""
    # Use last 20 messages to avoid overflowing context
    recent = historico[-20:]
    lines = []
    for msg in recent:
        label = usuario if msg["role"] == "user" else "Assistente RH"
        lines.append(f"[{label}]: {msg['conteudo']}")
    return "\n".join(lines)


def get_hr_response(
    mensagem: str,
    usuario: str,
    historico: list,
    contador_mensagens: int = 0,
) -> str:
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )

    backstory = BACKSTORY_BASE.format(usuario=usuario)

    agente_rh = Agent(
        role="Assistente de Recursos Humanos",
        goal=f"Responder dúvidas e auxiliar {usuario} em temas de RH com continuidade de conversa",
        backstory=backstory,
        llm=llm,
        verbose=False,
        max_iter=3,
    )

    historico_str = _build_history_context(historico, usuario)

    if historico_str:
        descricao_task = (
            f"Histórico da conversa com {usuario}:\n{historico_str}\n\n"
            f"Pergunta atual de {usuario}: {mensagem}"
        )
    else:
        descricao_task = f"Pergunta de {usuario}: {mensagem}"

    if contador_mensagens >= 6:
        descricao_task += (
            "\n\nAo final da resposta, mencione discretamente que para assuntos "
            "mais específicos ou urgentes, o colaborador pode abrir um chamado direto "
            "com a equipe de RH."
        )

    tarefa = Task(
        description=descricao_task,
        expected_output=(
            "Resposta clara, objetiva e empática em português do Brasil, "
            "mantendo continuidade com o histórico da conversa."
        ),
        agent=agente_rh,
    )

    crew = Crew(agents=[agente_rh], tasks=[tarefa], verbose=False)
    resultado = crew.kickoff()
    return str(resultado)
