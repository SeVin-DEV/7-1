import os
import importlib.util


ACTIVE_TOOLS = {}


def initialize_bus(app, manifest):
    """
    Preloads available tool file paths for dynamic execution.
    """

    global ACTIVE_TOOLS

    ACTIVE_TOOLS.clear()

    tool_names = manifest.split(",") if manifest else []

    for name in tool_names:
        path = f"tools/{name}.py"

        if os.path.exists(path):
            ACTIVE_TOOLS[name] = path

    if not hasattr(app, "extra_instructions"):
        app.extra_instructions = []

    app.extra_instructions.append(
        f"TOOL_BUS_ACTIVE: Tools Loaded | [{manifest}]"
    )


def call(tool_name, args=None):
    """
    Dynamically loads and executes tool module.
    Engine contract: args MUST be dict.
    """

    if not tool_name:
        return "TOOL_ERROR: Missing tool name."

    args = args or {}

    try:
        if tool_name not in ACTIVE_TOOLS:
            return f"TOOL_ERROR: '{tool_name}' not registered."

        spec = importlib.util.spec_from_file_location(
            tool_name,
            ACTIVE_TOOLS[tool_name]
        )

        if spec is None or spec.loader is None:
            return f"TOOL_ERROR: Failed to load spec for {tool_name}"

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "run"):
            return f"TOOL_ERROR: '{tool_name}' missing run(args) function."

        return module.run(args)

    except Exception as e:
        return f"TOOL_EXEC_ERROR: {str(e)}"
