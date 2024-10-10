from typing import List, Text
from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START
from chatbot.backend import retriever, prompt_controller, llm
from loguru import logger


### State
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: Text
    generation: Text
    in_lang: Text
    out_lang: Text
    trans_sent: Text
    role: Text
    prompt_template: PromptTemplate
    documents: List[Text]


### Nodes
def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    try:
        question = state["question"]
        logger.info(f"Running retrieval for question {question}...")
        docs = retriever.invoke(question)
        assert docs, f"No document found for question {question}"
    except AssertionError as e:
        logger.warning(f"{type(e).__name__}: {e}")
        state["documents"] = []

    else:
        logger.success(f"Found documents {docs} for question {question}")
        state["documents"] = docs
    return state


def generate(state):
    """
    Generate answer using RAG on retrieved documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    question = state["question"]
    prompt_template = state["prompt_template"]
    documents = state.get("documents", [])
    logger.info(f"Generating answer for question {question}...")
    # RAG generation
    rag_chain = prompt_template | llm
    generation = rag_chain.invoke({"documents": documents, "question": question})
    return dict(
        documents=documents,
        question=question,
        generation=generation,
        role=state["role"],
    )


def translate(state):
    in_lang = state["in_lang"]
    out_lang = state["out_lang"]
    trans_sent = state["trans_sent"]
    p_template = prompt_controller.translation.invoke(
        {"in_lang": in_lang, "out_lang": out_lang, "input": trans_sent}
    )
    print(p_template.to_string())
    generation = llm.invoke(p_template.to_string())
    return dict(trans_sent=generation)


def route_role(state):
    role = state["role"]
    role_dict = {
        "Researcher": "researcher",
        "Stand-up comedian": "comedian",
        "Motivational speaker": "speaker",
        "Son": "son",
    }
    role = role_dict.get(role, "")
    if not role:
        role_detector = prompt_controller.role_detector | llm
        generation = role_detector.invoke(dict(question=state["question"])).content
        role = role_dict.get(generation, "son")
    logger.info(f"Chatbot role: {role}")
    template = prompt_controller.__getattribute__(role)
    logger.info(f"Using template {template}")
    return dict(
        prompt_template=template,
        question=state["question"],
        role=role,
    )


def detect_language(state): ...


workflow = StateGraph(GraphState)
workflow.add_node("route_role", route_role)
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("generate", generate)  # generate
# workflow.add_node("translate", translate)  # translate
workflow.add_edge(START, "route_role")
workflow.add_edge("route_role", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()


def run_workflow(
    question: Text,
    role: Text,
    verbose: bool = False,
):
    inputs = dict(
        question=question,
        role=role,
    )
    outputs = app.stream(inputs)
    if verbose:
        for output in outputs:
            for k, v in output.items():
                logger.info(f"{k}: {v}")
        generation = output['generate']
        return f"{generation['generation'].content}\nRole: {generation['role']}"

    final_result = list(outputs)[-1]
    logger.info(f"Final output: {final_result}")
    generation = final_result["generate"]
    return f"{generation['generation'].content}\nRole: {generation['role']}"
