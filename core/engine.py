import os
import json
from core.persistence import get_identity_content, load_json, save_json
from core.manual_manager import audit_tool_specs
from core.belief_graph import resolve_conflicts, prune_low_value_nodes


MAX_CYCLES = 4


def parse_tool_call(raw: str):
    """
    Parses:
    USE_TOOL: tool_name | key=value, key2=value2

    Returns:
        (tool_name: str | None, args: dict)
    """
    try:
        payload = raw.split(":", 1)[1].strip()

        if "|" in payload:
            name, arg_str = payload.split("|", 1)
            args = {}

            for pair in arg_str.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    args[k.strip()] = v.strip()

            return name.strip(), args

        return payload.strip(), {}

    except Exception:
        return None, {}


async def run_cognitive_cycle(app, client, user_input):
    """
    THE CPU CORE (v4.0)

    Full cognitive lifecycle:
    - Load state
    - Maintain beliefs
    - Think
    - Decide
    - Act (tool or shell)
    - Observe
    - Repeat (bounded)
    - Persist
    """

    try:
        # === LOAD STATE ===
        history = load_json("chat_history.json", [])
        beliefs = load_json("belief_graph.json", {})

        identity = get_identity_content("soul.md")

        patches = os.getenv("SVN_ACTIVE_PATCHES", "None")
        tools = os.getenv("SVN_ACTIVE_TOOLS", "None")

        # === MAINTENANCE ===
        beliefs = resolve_conflicts(beliefs)
        beliefs = prune_low_value_nodes(beliefs)

        # === BUILD WORKING CONTEXT ===
        working_messages = [
            {
                "role": "system",
                "content": f"""
{identity}

[ACTIVE_PATCHES]
{patches}

[AVAILABLE_TOOLS]
{tools}

[KNOWN_BELIEFS]
{json.dumps(beliefs, indent=2)}

[COGNITIVE_PROTOCOL]
You operate in a loop:
1. Think about the problem
2. Decide if action is needed
3. If needed, choose ONE of:
   NEED_TOOL: tool_name
   USE_TOOL: tool_name | key=value
   EXEC: command
4. Otherwise, provide the final answer

Rules:
- Be precise
- Do not explain when issuing commands
- Only output ONE command when acting
"""
            },
            *history[-6:],
            {"role": "user", "content": user_input}
        ]

        final_answer = None
        last_msg = None

        # === COGNITIVE LOOP ===
        for _ in range(MAX_CYCLES):

            # === THINK ===
            res = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=working_messages,
                temperature=0.3
            )

            msg = res.choices[0].message.content.strip()
            last_msg = msg

            # Log internal reasoning step
            working_messages.append({
                "role": "assistant",
                "content": msg
            })

            # === DECISION TREE ===

            # --- TOOL DISCOVERY ---
            if msg.startswith("NEED_TOOL:"):
                tool_name = msg.split(":", 1)[-1].strip().replace(".py", "")

                manual_data, status = audit_tool_specs(tool_name)

                if status != "SUCCESS" or not manual_data:
                    final_answer = f"CPU_HALT: Tool '{tool_name}' unavailable."
                    break

                manual_text = manual_data.get("manual_text", "")

                working_messages.append({
                    "role": "system",
                    "content": f"""
[TOOL_MANUAL:{tool_name}]
{manual_text}

Construct the correct command.
Output ONLY one of:
USE_TOOL: tool_name | key=value
EXEC: command
"""
                })

                continue

            # --- TOOL EXECUTION ---
            elif msg.startswith("USE_TOOL:"):
                tool_name, args = parse_tool_call(msg)

                if not tool_name:
                    working_messages.append({
                        "role": "system",
                        "content": "[TOOL_ERROR] Invalid tool format."
                    })
                    continue

                try:
                    result = app.tools_bus.call(tool_name, args)
                except Exception as e:
                    result = f"TOOL_ERROR: {str(e)}"

                working_messages.append({
                    "role": "system",
                    "content": f"""
[TOOL_RESULT:{tool_name}]
{result}
"""
                })

                continue

            # --- SHELL EXECUTION ---
            elif msg.startswith("EXEC:"):
                command = msg.split(":", 1)[-1].strip()

                try:
                    result = app.patches_bus.call(command)
                except Exception as e:
                    result = f"SHELL_ERROR: {str(e)}"

                working_messages.append({
                    "role": "system",
                    "content": f"""
[SHELL_RESULT]
{result}
"""
                })

                continue

            # --- FINAL RESPONSE ---
            else:
                final_answer = msg
                break

        # === FALLBACK ===
        if not final_answer:
            final_answer = last_msg or "CPU_FALLBACK: No response generated."

        # === PERSISTENCE ===
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": final_answer})

        save_json("chat_history.json", history)
        save_json("belief_graph.json", beliefs)

        return final_answer, False

    except Exception as e:
        return f"CPU_EXCEPTION: {str(e)}", False
