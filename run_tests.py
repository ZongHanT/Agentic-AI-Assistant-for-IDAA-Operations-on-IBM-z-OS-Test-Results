"""
Regression test runner for agent API calls.

Usage (from the workspace root):
    python test_utils/run_tests.py [--url URL] [--output FILE] [--no-ssl-verify]

Each entry in test_questions.TESTS defines one question. The script sends it to
the API, records the HTTP status, response time, and the final AI message, then
writes a Markdown and JSON report to disk.

To add, remove, or edit test cases, edit test_utils/test_questions.py only —
no changes to this file are needed.
"""

import argparse
import asyncio
import json
import ssl
import time
import uuid
from datetime import datetime
from pathlib import Path

import aiohttp
import certifi

from test_questions import TESTS


def create_ssl_context(verify_ssl=True):
    """Build an SSL context. Pass False to skip verification (self-signed certs)."""
    ctx = ssl.create_default_context()
    if verify_ssl is False:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    elif isinstance(verify_ssl, str):
        ctx = ssl.create_default_context(cafile=verify_ssl)
    else:
        ctx = ssl.create_default_context(cafile=certifi.where())
    return ctx


# ---------------------------------------------------------------------------
# Configuration — edit these values to change test defaults
# ---------------------------------------------------------------------------
DEFAULT_AGENT = "db2z_agent"
DEFAULT_DB_ID = "77ad05ed-3e5a-4412-8b66-771d0cd1f48a"
DEFAULT_URL = "https://127.0.0.1:8000"
ENDPOINT = "/api/v1/chat"


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------

def _build_payload(test: dict) -> dict:
    return {
        "agent": test.get("agent", DEFAULT_AGENT),
        "thread_id": str(uuid.uuid4()),  # Fresh thread per test — prevents context bleed and cache hits
        "messages": [{"role": "user", "content": test["question"]}],
        "context": {"db_id": test.get("db_id", DEFAULT_DB_ID)},
        "stream": True,  # Enable streaming to capture tool calls
    }


def _extract_tool_info(response_body: dict):
    """Extract the last successful SQL query or tool execution from the response.
    
    Returns a dict with:
      - type: "sql", "tool", or None
      - content: the SQL query text, tool info dict, or None
      - tool_name: name of the tool (for non-SQL tools)
    
    The API response structure for non-streaming mode follows the LangGraph streaming format.
    Tool calls are embedded in choices[].delta.step_details or choices[].message structures.
    
    This function looks for:
      1. Tool calls in step_details (from streaming deltas)
      2. Tool calls in message objects (from chat completions)
      3. SQL queries in tool arguments
    """
    result: dict = {"type": None, "content": None, "tool_name": None}
    
    if not isinstance(response_body, dict):
        return result
    
    # The response follows the OpenAI-style format with choices array
    choices = response_body.get("choices", [])
    if not choices:
        return result
    
    # Process choices in reverse to find the most recent tool call
    for choice in reversed(choices):
        # Check for delta.step_details (streaming format with tool calls)
        delta = choice.get("delta", {})
        step_details = delta.get("step_details", {})
        
        if step_details and step_details.get("type") == "tool_calls":
            # Extract tool_calls from step_details
            tool_calls = step_details.get("tool_calls", [])
            if tool_calls:
                # Get the last tool call
                last_tool_call = tool_calls[-1]
                tool_name = last_tool_call.get("name", "")
                
                # Extract arguments - they might be in 'args' or 'function.arguments'
                tool_args = last_tool_call.get("args", {})
                if not tool_args and "function" in last_tool_call:
                    # Handle OpenAI-style function call format
                    func = last_tool_call["function"]
                    tool_name = func.get("name", tool_name)
                    args_str = func.get("arguments", "{}")
                    try:
                        tool_args = json.loads(args_str) if isinstance(args_str, str) else args_str
                    except json.JSONDecodeError:
                        tool_args = {}
                
                # Check if it's a SQL query tool
                if tool_name == "sql_db_query" and "query" in tool_args:
                    result["type"] = "sql"
                    result["content"] = tool_args["query"]
                    result["tool_name"] = tool_name
                    return result
                
                # Other tools - capture name and parameters
                elif tool_name:
                    result["type"] = "tool"
                    result["tool_name"] = tool_name
                    result["content"] = tool_args
                    return result
        
        # Check for message.tool_calls (chat completion format)
        message = choice.get("message", {})
        if message:
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                last_tool_call = tool_calls[-1]
                tool_name = last_tool_call.get("name", "")
                tool_args = last_tool_call.get("args", {})
                
                # Handle function call format
                if not tool_args and "function" in last_tool_call:
                    func = last_tool_call["function"]
                    tool_name = func.get("name", tool_name)
                    args_str = func.get("arguments", "{}")
                    try:
                        tool_args = json.loads(args_str) if isinstance(args_str, str) else args_str
                    except json.JSONDecodeError:
                        tool_args = {}
                
                if tool_name == "sql_db_query" and "query" in tool_args:
                    result["type"] = "sql"
                    result["content"] = tool_args["query"]
                    result["tool_name"] = tool_name
                    return result
                elif tool_name:
                    result["type"] = "tool"
                    result["tool_name"] = tool_name
                    result["content"] = tool_args
                    return result
    
    return result


def _extract_model_name(response_body: dict) -> str | None:
    """Extract the model name from an OpenAI-style API response.

    Looks for the top-level ``model`` field that the engine echoes back from
    the underlying LLM provider (e.g. ``gpt-oss-120b``, ``granite-3-8b``).
    Returns None when the field is absent or empty.
    """
    if not isinstance(response_body, dict):
        return None
    model = response_body.get("model")
    if isinstance(model, str) and model.strip():
        return model.strip()
    return None


def _extract_ai_message(response_body: dict) -> str:
    """Pull the final AI text out of the response.

    Handles two shapes:
      - OpenAI chat.completion: {"choices": [{"message": {"role": "assistant", "content": "..."}}]}
      - Messages list:          {"messages": [...]} or a bare list of message dicts
    """
    # Shape 1: OpenAI chat.completion
    choices = response_body.get("choices") if isinstance(response_body, dict) else None
    if choices:
        for choice in choices:
            content = choice.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()

    # Shape 2: messages list
    messages = response_body if isinstance(response_body, list) else response_body.get("messages", [])
    for msg in reversed(messages):
        role = msg.get("role", "") or msg.get("type", "")
        if role in ("ai", "assistant"):
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()
            if isinstance(content, list):
                parts = [c.get("text", "") for c in content if isinstance(c, dict)]
                combined = " ".join(p for p in parts if p).strip()
                if combined:
                    return combined

    return "(no AI message found in response)"


async def run_test(
    session: aiohttp.ClientSession,
    base_url: str,
    test: dict,
) -> tuple[dict, str | None]:
    """Run a single test and return ``(result_dict, model_name_or_None)``."""
    url = base_url.rstrip("/") + ENDPOINT
    payload = _build_payload(test)
    result = {
        "name": test["name"],
        "question": test["question"],
        "agent": test.get("agent", DEFAULT_AGENT),
        "status": None,
        "elapsed_s": None,
        "answer": None,
        "error": None,
        "last_tool_info": None,
    }
    model_name: str | None = None
    t0 = time.perf_counter()
    try:
        async with session.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=None),
        ) as resp:
            result["status"] = resp.status
            
            # Handle streaming response (newline-delimited JSON)
            if resp.content_type == "application/x-ndjson":
                all_chunks = []
                # Track per-message-id content so we pick up the last complete AI message,
                # not a concatenation of every intermediate delta from every graph node.
                message_buffers: dict[str, str] = {}
                last_message_id: str | None = None

                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        all_chunks.append(chunk)

                        # Capture model name from the first chunk that carries it
                        if model_name is None:
                            model_name = _extract_model_name(chunk)

                        # Accumulate streaming token deltas, grouped by message id.
                        # Keepalive chunks (id="keepalive", empty content) are ignored.
                        if chunk.get("object") == "thread.message.delta":
                            msg_id = chunk.get("id", "")
                            if msg_id == "keepalive":
                                pass
                            else:
                                choices = chunk.get("choices", [])
                                for choice in choices:
                                    content = choice.get("delta", {}).get("content", "")
                                    if content:
                                        message_buffers[msg_id] = message_buffers.get(msg_id, "") + content
                                        last_message_id = msg_id

                        # Capture complete messages (chat.completion) emitted by the updates path.
                        # Granite and cached responses often arrive this way instead of as deltas.
                        elif chunk.get("object") == "chat.completion":
                            choices = chunk.get("choices", [])
                            for choice in choices:
                                content = choice.get("message", {}).get("content", "")
                                if content:
                                    msg_id = chunk.get("id", f"completion-{len(message_buffers)}")
                                    message_buffers[msg_id] = content
                                    last_message_id = msg_id

                    except json.JSONDecodeError:
                        continue

                result["elapsed_s"] = round(time.perf_counter() - t0, 2)
                # Use the last AI message seen (either streamed token-by-token or as a complete update)
                if last_message_id is not None and message_buffers.get(last_message_id):
                    result["answer"] = message_buffers[last_message_id].strip()
                else:
                    result["answer"] = "(no AI message found in response)"

                # Extract tool info from all chunks
                for chunk in all_chunks:
                    tool_info = _extract_tool_info(chunk)
                    if tool_info and tool_info.get("type"):
                        result["last_tool_info"] = tool_info
                        # Keep looking to find the last tool call
            
            # Handle non-streaming JSON response (fallback)
            elif resp.content_type == "application/json":
                result["elapsed_s"] = round(time.perf_counter() - t0, 2)
                body = await resp.json()
                model_name = _extract_model_name(body)
                result["answer"] = _extract_ai_message(body)
                result["last_tool_info"] = _extract_tool_info(body)
            
            else:
                result["elapsed_s"] = round(time.perf_counter() - t0, 2)
                result["answer"] = await resp.text()
    except asyncio.TimeoutError:
        result["elapsed_s"] = round(time.perf_counter() - t0, 2)
        result["error"] = "Request timed out"
    except Exception as exc:
        result["elapsed_s"] = round(time.perf_counter() - t0, 2)
        result["error"] = str(exc)
    return result, model_name


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _status_icon(result: dict) -> str:
    if result["error"]:
        return "❌"
    if result["status"] == 200:
        return "✅"
    return "⚠️"


def build_markdown_report(
    results: list,
    base_url: str,
    run_ts: str,
    model_name: str | None = None,
) -> str:
    total = len(results)
    passed = sum(1 for r in results if r["status"] == 200 and not r["error"])
    failed = total - passed

    model_line = f"**Model:** `{model_name}`  \n" if model_name else ""

    lines = [
        f"# Agent API Test Report",
        f"",
        f"**Run:** {run_ts}  ",
        f"**Target:** `{base_url}`  ",
        f"{model_line}**Results:** {passed}/{total} passed",
        f"",
        "---",
        "",
    ]

    for i, r in enumerate(results, 1):
        icon = _status_icon(r)
        lines += [
            f"## {i}. {icon} {r['name']}",
            f"",
            f"**Agent:** `{r['agent']}`  ",
            f"**Question:** {r['question']}  ",
            f"**HTTP status:** `{r['status']}`  ",
            f"**Elapsed:** {r['elapsed_s']}s  ",
            f"",
        ]
        
        # Add tool/SQL information if available
        tool_info = r.get("last_tool_info")
        if tool_info and tool_info.get("type"):
            if tool_info["type"] == "sql":
                lines += [
                    f"**Last SQL Query:**",
                    f"```sql",
                    f"{tool_info['content']}",
                    f"```",
                    f"",
                ]
            elif tool_info["type"] == "tool":
                tool_name = tool_info.get("tool_name", "unknown")
                tool_params = tool_info.get("content", {})
                lines += [
                    f"**Last Tool Used:** `{tool_name}`",
                    f"",
                    f"Parameters:",
                    f"```json",
                    f"{json.dumps(tool_params, indent=2)}",
                    f"```",
                    f"",
                ]
        
        if r["error"]:
            lines += [f"**Error:** {r['error']}", ""]
        else:
            lines += [
                f"**Answer:**",
                f"",
                f"> {r['answer'].replace(chr(10), '  \n> ')}",
                f"",
            ]
        lines.append("---")
        lines.append("")

    footer_model = f" | Model: {model_name}" if model_name else ""
    lines += [
        f"*Total: {total} | Passed: {passed} | Failed: {failed}{footer_model}*",
    ]
    return "\n".join(lines)


def build_json_report(
    results: list,
    base_url: str,
    run_ts: str,
    model_name: str | None = None,
) -> dict:
    return {
        "run_timestamp": run_ts,
        "target_url": base_url,
        "model": model_name,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == 200 and not r["error"]),
            "failed": sum(1 for r in results if r["status"] != 200 or r["error"]),
        },
        "results": results,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main(base_url: str, output_path: Path, verify_ssl):
    ssl_ctx = create_ssl_context(verify_ssl)
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)

    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []
    # Collect the first non-None model name seen across all test responses
    detected_model: str | None = None

    print(f"\nRunning {len(TESTS)} tests against {base_url}\n{'─' * 60}")

    async with aiohttp.ClientSession(connector=connector) as session:
        for i, test in enumerate(TESTS, 1):
            print(f"[{i}/{len(TESTS)}] {test['name']} ...", end=" ", flush=True)
            result, model_name = await run_test(session, base_url, test)
            results.append(result)
            if detected_model is None and model_name:
                detected_model = model_name
            icon = _status_icon(result)
            print(f"{icon}  ({result['elapsed_s']}s, HTTP {result['status']})")

    # Write Markdown report
    md_path = output_path.with_suffix(".md")
    md_path.write_text(
        build_markdown_report(results, base_url, run_ts, detected_model),
        encoding="utf-8",
    )

    # Write JSON report alongside
    json_path = output_path.with_suffix(".json")
    json_path.write_text(
        json.dumps(
            build_json_report(results, base_url, run_ts, detected_model),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    passed = sum(1 for r in results if r["status"] == 200 and not r["error"])
    model_label = f"  Model:   {detected_model}" if detected_model else ""
    print(f"\n{'─' * 60}")
    print(f"Results: {passed}/{len(results)} passed")
    if model_label:
        print(model_label)
    print(f"Report:  {md_path}")
    print(f"JSON:    {json_path}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run agent API regression tests")
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Base URL of the engine API (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--output",
        default="test_utils/test_report",
        help="Output file path without extension (default: test_utils/test_report)",
    )
    parser.add_argument(
        "--no-ssl-verify",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            base_url=args.url,
            output_path=Path(args.output),
            verify_ssl=not args.no_ssl_verify,
        )
    )
