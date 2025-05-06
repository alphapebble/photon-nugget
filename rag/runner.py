from retriever.base import get_context_documents
from model.llm_factory import get_llm
from prompts.template_loader import load_structured_prompt, render_prompt  # rename the file if needed

llm = get_llm()

def rag_answer(user_query: str) -> str:
    context_docs = get_context_documents(user_query)
    context = "\n".join(context_docs[:3])

    config, prompt_template = load_structured_prompt("solar_rag")  # expects prompts/solar_rag.prompt
    prompt = render_prompt(prompt_template, {
        "query": user_query,
        "context": context,
    })

    return llm.generate(prompt)
