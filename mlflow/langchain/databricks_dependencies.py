from typing import Dict, Optional, Set

_DATABRICKS_DEPENDENCY_KEY = "databricks_dependency"
_DATABRICKS_VECTOR_SEARCH_INDEX_NAME_KEY = "databricks_vector_search_index_name"
_DATABRICKS_VECTOR_SEARCH_ENDPOINT_NAME_KEY = "databricks_vector_search_endpoint_name"
_DATABRICKS_EMBEDDINGS_ENDPOINT_NAME_KEY = "databricks_embeddings_endpoint_name"
_DATABRICKS_LLM_ENDPOINT_NAME_KEY = "databricks_llm_endpoint_name"
_DATABRICKS_CHAT_ENDPOINT_NAME_KEY = "databricks_chat_endpoint_name"


def _assign_value_or_append_to_list(d, key, value):
    if key in d:
        if isinstance(d[key], list):
            d[key].append(value)
        else:
            d[key] = [d[key], value]
    else:
        d[key] = value
    return d


def _extract_databricks_dependencies_from_retriever(retriever, dependency_dict) -> Dict[str, str]:
    import langchain

    if hasattr(retriever, "vectorstore") and hasattr(retriever.vectorstore, "embeddings"):
        vectorstore = retriever.vectorstore
        embeddings = vectorstore.embeddings

        if isinstance(vectorstore, langchain.vectorstores.DatabricksVectorSearch):
            index = vectorstore.index
            _assign_value_or_append_to_list(
                dependency_dict, _DATABRICKS_VECTOR_SEARCH_INDEX_NAME_KEY, index.name
            )
            _assign_value_or_append_to_list(
                dependency_dict, _DATABRICKS_VECTOR_SEARCH_ENDPOINT_NAME_KEY, index.endpoint_name
            )

        if isinstance(embeddings, langchain.embeddings.DatabricksEmbeddings):
            _assign_value_or_append_to_list(
                dependency_dict, _DATABRICKS_EMBEDDINGS_ENDPOINT_NAME_KEY, embeddings.endpoint
            )
        elif (
            hasattr(vectorstore, "_is_databricks_managed_embeddings")
            and callable(getattr(vectorstore, "_is_databricks_managed_embeddings"))
            and vectorstore._is_databricks_managed_embeddings()
        ):
            _assign_value_or_append_to_list(
                dependency_dict,
                _DATABRICKS_EMBEDDINGS_ENDPOINT_NAME_KEY,
                "_is_databricks_managed_embeddings",
            )

    return dependency_dict


def _extract_databricks_dependencies_from_llm(llm, dependency_dict) -> Dict[str, str]:
    import langchain

    if isinstance(llm, langchain.llms.Databricks):
        _assign_value_or_append_to_list(
            dependency_dict, _DATABRICKS_LLM_ENDPOINT_NAME_KEY, llm.endpoint_name
        )
    return dependency_dict


def _extract_databricks_dependencies_from_chat_model(chat_model, dependency_dict) -> Dict[str, str]:
    import langchain

    if isinstance(chat_model, langchain.chat_models.ChatDatabricks):
        _assign_value_or_append_to_list(
            dependency_dict, _DATABRICKS_CHAT_ENDPOINT_NAME_KEY, chat_model.endpoint
        )
    return dependency_dict


def _extract_dpendency_dict_from_lc_model(lc_model, dependency_dict) -> Dict[str, str]:
    if hasattr(lc_model, "retriever"):
        dependency_dict = _extract_databricks_dependencies_from_retriever(
            lc_model.retriever, dependency_dict
        )

    if hasattr(
        lc_model, "llm_chain"
    ):  # StuffDocumentsChain, MapRerankDocumentsChain, MapReduceDocumentsChain
        dependency_dict = _extract_databricks_dependencies_from_llm(
            lc_model.llm_chain.llm, dependency_dict
        )
    if hasattr(lc_model, "question_generator"):  # BaseConversationalRetrievalChain
        dependency_dict = _extract_databricks_dependencies_from_llm(
            lc_model.question_generator.llm, dependency_dict
        )

    if hasattr(lc_model, "initial_llm_chain") and hasattr(
        lc_model, "refine_llm_chain"
    ):  # RefineDocumentsChain
        dependency_dict = _extract_databricks_dependencies_from_llm(
            lc_model.initial_llm_chain.llm, dependency_dict
        )
        dependency_dict = _extract_databricks_dependencies_from_llm(
            lc_model.refine_llm_chain.llm, dependency_dict
        )

    if hasattr(lc_model, "combine_documents_chain"):  # RetrievalQA, ReduceDocumentsChain
        dependency_dict = _extract_dpendency_dict_from_lc_model(
            lc_model.combine_documents_chain, dependency_dict
        )
    if hasattr(lc_model, "combine_docs_chain"):  # BaseConversationalRetrievalChain
        dependency_dict = _extract_dpendency_dict_from_lc_model(
            lc_model.combine_docs_chain, dependency_dict
        )

    if (
        hasattr(lc_model, "collapse_documents_chain")
        and lc_model.collapse_documents_chain is not None
    ):  # ReduceDocumentsChain
        dependency_dict = _extract_dpendency_dict_from_lc_model(
            lc_model.collapse_documents_chain, dependency_dict
        )

    if hasattr(lc_model, "chat_model"):
        dependency_dict = _extract_databricks_dependencies_from_chat_model(
            lc_model.chat_model, dependency_dict
        )
    return dependency_dict


def _traverse_runnable(
    lc_model, dependency_dict: Dict[str, str], visited: Set[str]
) -> (Dict[str, str], Set[str]):
    import langchain_core

    current_object_id = id(lc_model)
    if current_object_id in visited:
        return dependency_dict, visited

    # Visit the current object
    visited.add(current_object_id)
    dependency_dict = _extract_dpendency_dict_from_lc_model(lc_model, dependency_dict)

    if isinstance(lc_model, langchain_core.runnables.RunnableSerializable):
        # Visit the returned graph
        for node in lc_model.get_graph().nodes.values():
            dependency_dict, visited = _traverse_runnable(node.data, dependency_dict, visited)
    else:
        # This is a leaf node
        pass
    return dependency_dict, visited


def _detect_databricks_dependencies(lc_model, visited: Optional[Set[str]] = None) -> Dict[str, str]:
    """
    Detects the databricks dependencies of a langchain model and returns a dictionary of
    detected endpoint names and index names.

    lc_model can be an arbirary [chain that is built with LCEL](https://python.langchain.com
    /docs/modules/chains#lcel-chains), which is a langchain_core.runnables.RunnableSerializable.
    If a [legacy chain constructed by subclassing from a legacy Chain
    class](https://python.langchain.com/docs/modules/chains#legacy-chains) is also a
    langchain_core.runnables.RunnableSerializable, it is also supported.

    For an LCEL chain, all the langchain_core.runnables.RunnableSerializable nodes will be
    traversed.

    If a retriever is found, it will be used to extract the databricks vector search and embeddings
    dependencies. If an llm is found, it will be used to extract the databricks llm dependencies.
    If a chat_model is found, it will be used to extract the databricks chat dependencies.
    """
    if visited is None:
        visited = set()
    dependency_dict = {}
    visited = set()
    return _traverse_runnable(lc_model, dependency_dict, visited)[0]
