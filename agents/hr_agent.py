from crewai import LLM, Agent, Task, Crew
from crewai.tools import tool
import os

from rag.retriever import retrieve

SENSITIVE_TOPICS = [
    "salário", "salario", "remuneração", "remuneracao",
    "assédio", "assedio", "discriminação", "discriminacao",
    "demissão", "demissao", "desligamento",
    "dados médicos", "dados medicos", "saúde mental", "saude mental",
    "denúncia", "denuncia", "retaliação", "retaliacao",
    "avaliação individual", "avaliacao individual",
]

SENSITIVE_RESPONSE = (
    "Este assunto envolve informações sensíveis e deve ser tratado diretamente "
    "com a equipe de RH, de forma confidencial e segura.\n\n"
    "Gostaria que eu **abra um chamado** para que um especialista de RH entre em contato com você?"
)


def _is_sensitive(mensagem: str) -> bool:
    lower = mensagem.lower()
    return any(topic in lower for topic in SENSITIVE_TOPICS)


def _build_history_block(historico: list, usuario: str) -> str:
    if not historico:
        return ""
    recent = historico[-10:]
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
) -> dict:

    # Tópico sensível → escala imediatamente sem passar pelo LLM
    if _is_sensitive(mensagem):
        return {
            "resposta": SENSITIVE_RESPONSE,
            "deve_escalar": True,
            "fundamentada": True,
            "fontes": [],
            "sem_resposta": False,
        }

    # Estado mutável rastreado pelas tools (closures)
    rag_sources: list[str] = []
    sem_resposta: list[bool] = [False]

    @tool("buscar_conhecimento_rh")
    def buscar_conhecimento_rh(query: str) -> str:
        """
        Busca informações na base de conhecimento de RH sobre políticas internas,
        benefícios, férias, licenças, onboarding, performance, compliance, CLT,
        abertura de chamados e people analytics.

        Use esta ferramenta SOMENTE quando o usuário fizer uma pergunta ou pedido
        que exija busca em documentos de RH.
        NÃO use para saudações, agradecimentos ou conversa casual.
        """
        resultado = retrieve(query, n_results=4)

        if not resultado["found"]:
            sem_resposta[0] = True
            return (
                "BASE_SEM_RESPOSTA: Não encontrei informações relevantes na base de "
                "conhecimento para esta pergunta. Informe ao usuário que não possui "
                "essa informação e pergunte se ele gostaria de abrir um chamado com o RH."
            )

        for src in resultado["sources"]:
            if src not in rag_sources:
                rag_sources.append(src)

        chunks_text = "\n\n---\n\n".join(
            f"[{c['meta'].get('doc_id', '')} | {c['meta'].get('section', '')}]\n{c['text']}"
            for c in resultado["chunks"]
        )
        return f"FONTES: {', '.join(resultado['sources'])}\n\nCONTEÚDO:\n{chunks_text}"

    # Contexto de histórico vindo do banco
    history_block = _build_history_block(historico, usuario)
    is_new = len(historico) == 0
    nome = usuario.split()[0]

    hist_section = (
        f"\nHistórico da conversa:\n{history_block}\n"
        if history_block else ""
    )

    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.4,
    )

    agente_rh = Agent(
        role="Assistente de Recursos Humanos",
        goal=(
            f"Auxiliar {nome} EXCLUSIVAMENTE com dúvidas de RH, de forma precisa e sem alucinar."
        ),
        backstory=(
            f"Você é um assistente de RH inteligente da empresa, conversando com {nome}.\n\n"
            "## Quando usar a ferramenta 'buscar_conhecimento_rh':\n"
            "- O usuário fez uma pergunta sobre RH (férias, benefícios, políticas, onboarding, etc.)\n"
            "- O usuário pediu orientação sobre um processo interno\n"
            "- Existe intenção clara de obter informação de RH\n\n"
            "## Quando NÃO usar a ferramenta:\n"
            "- Saudações, agradecimentos ou respostas curtas ('oi', 'ok', 'obrigado', 'ótimo')\n"
            "- Conversa casual sem intenção de busca\n\n"
            "## Perguntas fora do escopo de RH:\n"
            "- Se a pergunta NÃO tiver relação com Recursos Humanos (ex: história, culinária, "
            "esportes, tecnologia geral, entretenimento, etc.), NUNCA responda com base no seu "
            "conhecimento geral.\n"
            "- Nestes casos, comece sua resposta com exatamente 'FORA_DO_ESCOPO:' e em seguida "
            "informe educadamente que você é especializado em RH e convide o usuário a fazer "
            "perguntas relacionadas a benefícios, férias, políticas, onboarding, performance "
            "ou abertura de chamados.\n\n"
            "## Regras gerais:\n"
            "- Responda SEMPRE em português do Brasil\n"
            f"- {'Esta é a primeira mensagem — pode cumprimentar o usuário.' if is_new else 'A conversa já está em andamento — vá direto ao ponto, sem repetir saudações.'}\n"
            "- Se a ferramenta retornar BASE_SEM_RESPOSTA: informe que não tem a informação "
            "e ofereça abrir um chamado com o RH\n"
            "- NUNCA invente políticas, números ou dados não encontrados na ferramenta\n"
            "- Seja empático, direto e objetivo"
        ),
        tools=[buscar_conhecimento_rh],
        llm=llm,
        verbose=False,
        max_iter=4,
    )

    tarefa = Task(
        description=(
            f"{hist_section}"
            f"\nMensagem de {nome}: {mensagem}\n\n"
            "Analise a mensagem:\n"
            "- Se for conversa casual (saudação, agradecimento, confirmação): responda "
            "naturalmente em 1-2 linhas, sem usar ferramentas.\n"
            "- Se for uma pergunta ou pedido sobre RH: use obrigatoriamente a ferramenta "
            "'buscar_conhecimento_rh' e elabore uma resposta completa e detalhada com base "
            "no conteúdo retornado. Inclua todos os passos, condições e orientações "
            "relevantes encontrados nos documentos. Use listas quando ajudar a organizar.\n"
            "- Se a pergunta NÃO tiver nenhuma relação com RH (ex: história, esportes, "
            "culinária, ciência, entretenimento, tecnologia geral): inicie sua resposta com "
            "exatamente 'FORA_DO_ESCOPO:' e redirecione educadamente o usuário para temas de RH. "
            "NÃO use ferramentas e NÃO responda a pergunta em si."
        ),
        expected_output=(
            "Para perguntas de RH: resposta detalhada, estruturada e fundamentada nos "
            "documentos retornados pela ferramenta, em português do Brasil. "
            "Para conversa casual: resposta curta e natural. "
            "Para perguntas fora do escopo: resposta começando com 'FORA_DO_ESCOPO:' "
            "redirecionando o usuário para temas de RH."
        ),
        agent=agente_rh,
    )

    crew = Crew(agents=[agente_rh], tasks=[tarefa], verbose=False)
    resposta_final = str(crew.kickoff()).strip()

    # Detecta pergunta fora do escopo de RH
    MARKER = "FORA_DO_ESCOPO:"
    if resposta_final.upper().startswith(MARKER.upper()):
        # Remove o marcador e limpa espaços
        resposta_final = resposta_final[len(MARKER):].strip()
        sem_resposta[0] = True

    # Detecta se o agente sinalizou necessidade de escalada
    deve_escalar = any(
        kw in resposta_final.lower()
        for kw in ["abrir um chamado", "equipe de rh", "escalar", "atendimento humano"]
    ) and sem_resposta[0]

    if contador_mensagens >= 6 and not deve_escalar and rag_sources:
        resposta_final += (
            "\n\n_Para assuntos mais específicos ou urgentes, você pode abrir um "
            "chamado diretamente com a equipe de RH._"
        )

    return {
        "resposta": resposta_final,
        "deve_escalar": deve_escalar,
        "fundamentada": not sem_resposta[0],
        "fontes": rag_sources,
        "sem_resposta": sem_resposta[0],
    }
