from retriever.retriever_lancedb import get_context_documents
from llm.llm_factory import get_llm
from .prompts.template_loader import load_structured_prompt, render_prompt

llm = get_llm()

def rag_answer(user_query: str) -> str:
    # Retrieve top N relevant context chunks
    context_docs = get_context_documents(user_query)
    context = "\n".join(context_docs[:3])  # Use top 3 hits

    # Load YAML + prompt template from file
    config, prompt_template = load_structured_prompt("solar_rag")

    # Fill in the template with user query and context
    prompt = render_prompt(prompt_template, {
        "query": user_query,
        "context": context,
    })

    # Generate response from selected LLM
    return llm.generate(prompt)
