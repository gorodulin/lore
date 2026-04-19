def handle_fact_request(store, method: str, params: dict) -> dict:
    """Dispatch a request method to the appropriate FactStore operation.

    Raises ValueError on unknown method.
    """
    if method == "find_facts":
        return _handle_find_facts(store, params)
    elif method == "read_fact":
        return _handle_read_fact(store, params)
    elif method == "create_fact":
        return _handle_create_fact(store, params)
    elif method == "edit_fact":
        return _handle_edit_fact(store, params)
    elif method == "delete_fact":
        return _handle_delete_fact(store, params)
    elif method == "validate":
        return _handle_validate(store, params)
    elif method == "ping":
        return {"status": "ok"}
    else:
        raise ValueError(f"Unknown method: {method}")


def _handle_find_facts(store, params: dict) -> dict:
    file_path = params.get("file_path", "")
    content = params.get("content")
    description = params.get("description")
    command = params.get("command")
    tools_param = params.get("tools")
    tools = tuple(tools_param) if tools_param is not None else None
    tags = params.get("tags")
    if not file_path and description is None and command is None and tools is None:
        raise ValueError("find_facts requires 'file_path', 'description', 'command', or 'tools' param")
    return store.find_matching_facts(file_path, content=content, description=description, command=command, tools=tools, tags=tags)


def _handle_read_fact(store, params: dict) -> dict:
    fact_id = params.get("fact_id")
    if not fact_id:
        raise ValueError("read_fact requires 'fact_id' param")
    fact = store.get_fact(fact_id)
    if fact is None:
        raise ValueError(f"Fact '{fact_id}' not found")
    return {"fact_id": fact_id, **fact}


def _handle_create_fact(store, params: dict) -> dict:
    fact_text = params.get("fact")
    if not fact_text:
        raise ValueError("create_fact requires 'fact' param")
    incl = params.get("incl")
    if not incl:
        raise ValueError("create_fact requires 'incl' param")
    skip = params.get("skip")
    tags = params.get("tags")
    fact_id = params.get("fact_id")
    return store.create_fact(fact_text, incl, skip=skip, fact_id=fact_id, tags=tags)


def _handle_edit_fact(store, params: dict) -> dict:
    fact_id = params.get("fact_id")
    if not fact_id:
        raise ValueError("edit_fact requires 'fact_id' param")
    return store.edit_fact(
        fact_id,
        fact_text=params.get("fact"),
        incl=params.get("incl"),
        skip=params.get("skip"),
        tags=params.get("tags"),
    )


def _handle_delete_fact(store, params: dict) -> dict:
    fact_id = params.get("fact_id")
    if not fact_id:
        raise ValueError("delete_fact requires 'fact_id' param")
    return store.delete_fact(fact_id)


def _handle_validate(store, params: dict) -> dict:
    return store.validate_all_facts()
