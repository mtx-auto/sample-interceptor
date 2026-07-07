"""
DIAL interceptor scaffold — all hooks exposed with comments.

Copy this file, rename the class, and fill in the # TODO sections
with your custom logic. Every hook has a default no-op implementation
in the base class; only override the ones you need.
"""

import logging

from aidial_interceptors_sdk.chat_completion.annotated_value import AnnotatedException
from aidial_interceptors_sdk.chat_completion.base import ChatCompletionInterceptor
from aidial_interceptors_sdk.chat_completion.element_path import ElementPath

log = logging.getLogger(__name__)


class SampleInterceptor(ChatCompletionInterceptor):
    """
    Generic scaffold interceptor.

    Lifecycle order per request:
        1. on_request          — full request dict (before messages hook)
        2. on_request_messages — just the messages list
        3. [request forwarded to upstream LLM]
        4. on_stream_start     — streaming begins
        5. on_response_choice  — called for every streamed chunk
        6. on_stream_end       — streaming finished normally
           on_stream_error     — streaming failed (instead of on_stream_end)
    """

    # ------------------------------------------------------------------ #
    # PRE-REQUEST HOOKS                                                    #
    # ------------------------------------------------------------------ #

    async def on_request(self, request: dict) -> dict:
        """
        Fires first, with the full raw request dict (OpenAI-compatible).

        Use this hook to:
        - Read top-level fields: model, temperature, max_tokens, stream, n, tools, etc.
        - Override model or parameters before they reach the upstream.
        - Store request-level state on self (e.g. self.n = request.get("n") or 1).
        - Reject the request early by raising HTTPException.

        Example — force temperature to 0:
            request["temperature"] = 0.0

        Example — read how many completions were requested:
            self.n = request.get("n") or 1
        """
        # TODO: add your request-level logic here
        log.debug("on_request: model=%s", request.get("model"))
        return request

    async def on_request_messages(self, messages: list[dict]) -> list[dict]:
        """
        Fires after on_request, with the messages list only.

        Each message is a dict with at minimum:
            {"role": "user"|"assistant"|"system"|"tool", "content": str | list}

        content can be a plain string or a list of content parts
        (text, image_url, tool_result, etc.).

        Use this hook to:
        - Inspect or transform message text.
        - Prepend / append a system prompt.
        - Block forbidden content (raise HTTPException to reject).
        - Anonymize PII before it reaches the LLM.

        Example — inject a system prompt if none exists:
            if not any(m["role"] == "system" for m in messages):
                messages.insert(0, {"role": "system", "content": "You are helpful."})

        Example — uppercase every user message:
            for msg in messages:
                if msg.get("role") == "user" and isinstance(msg.get("content"), str):
                    msg["content"] = msg["content"].upper()
        """
        # TODO: add your message-level logic here
        log.debug("on_request_messages: %d messages", len(messages))
        return messages

    # ------------------------------------------------------------------ #
    # STREAM LIFECYCLE HOOKS                                               #
    # ------------------------------------------------------------------ #

    async def on_stream_start(self) -> None:
        """
        Fires once, immediately before the first streamed chunk arrives.

        Use this hook to:
        - Open DIAL UI "stage" panels (progress sections visible in the chat UI).
        - Initialise per-response accumulators or buffers.
        - Start timers / span traces.

        Opening a stage (shows collapsible section in DIAL chat UI):
            with Stage(self.response._queue, 0, self.reserve_stage_index(0), "My Stage") as s:
                s.append_content("Processing…")
        """
        # TODO: initialise response-side state here
        log.debug("on_stream_start")

    async def on_stream_end(self) -> None:
        """
        Fires once after the last streamed chunk has been sent to the client
        (finish_reason received, no errors).

        Use this hook to:
        - Close any open DIAL UI stages.
        - Flush accumulated response text to an observability backend.
        - Record latency metrics.
        - Finalize any post-processing that needs the complete response.
        """
        # TODO: finalise response-side state here
        log.debug("on_stream_end")

    async def on_stream_error(self, error: AnnotatedException) -> None:
        """
        Fires instead of on_stream_end when the upstream returns an error
        or the stream is interrupted.

        Default behaviour: re-raise the error so the client receives it.
        Override to:
        - Log the error to an observability system.
        - Return a fallback response (don't re-raise).
        - Close any open DIAL UI stages gracefully.

        Example — log and re-raise:
            log.error("Stream error: %s", error.error)
            raise error.error
        """
        # TODO: handle stream errors here
        log.error("on_stream_error: %s", error.error)
        raise error.error

    # ------------------------------------------------------------------ #
    # POST-RESPONSE HOOK                                                   #
    # ------------------------------------------------------------------ #

    async def on_response_choice(
        self, path: ElementPath, choice: dict
    ) -> dict | list[dict]:
        """
        Fires for every streamed response chunk (one call per delta).

        `path.choice_idx` — which completion choice this chunk belongs to (0-based).
        `choice` structure (streaming delta format):
            {
                "index": 0,
                "delta": {"role": "assistant", "content": "Hello"},
                "finish_reason": null   # or "stop" / "length" on the last chunk
            }

        Return the modified choice dict, or a list of dicts to fan-out
        (e.g. inject an extra chunk before/after).

        Use this hook to:
        - Transform response text as it streams (e.g. de-anonymize tokens).
        - Buffer content until a safe boundary, then flush.
        - Add a watermark or suffix to the final chunk.
        - Drop chunks (return choice with empty delta content).

        Example — append " [intercepted]" to every text chunk:
            delta = choice.get("delta") or {}
            if content := delta.get("content"):
                delta["content"] = content + " [intercepted]"

        Example — suppress content on the last chunk (finish_reason present):
            if choice.get("finish_reason"):
                (choice.get("delta") or {})["content"] = ""
        """
        # TODO: add your response-chunk logic here
        delta = choice.get("delta") or {}
        if content := delta.get("content"):
            log.debug("on_response_choice[%s]: %d chars", path.choice_idx, len(content))
        return choice
