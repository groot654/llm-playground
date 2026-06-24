"""
Prompt engineering techniques
------------------------------
Each technique maps to a dynamically-built system prompt. The chat endpoint
calls `build_system_prompt(technique, custom_text)` to get the right system
message to prepend to the conversation.

Techniques:
  - zero_shot       : plain instruction, no examples
  - role            : assign the model an expert persona
  - few_shot        : give a couple of input/output examples to imitate
  - output_format   : force a specific structured output shape
  - step_by_step    : ask the model to reason in explicit steps
  - custom          : user supplies their own system prompt
"""

from typing import Dict, List

# Human-readable metadata used to populate the dropdown on the front-end.
TECHNIQUES: List[Dict[str, str]] = [
    {"id": "zero_shot", "label": "Zero-shot"},
    {"id": "role", "label": "Role prompting"},
    {"id": "few_shot", "label": "Few-shot"},
    {"id": "output_format", "label": "Output format"},
    {"id": "step_by_step", "label": "Step-by-step explanation"},
    {"id": "custom", "label": "Custom system prompt"},
]

VALID_TECHNIQUE_IDS = {t["id"] for t in TECHNIQUES}

# Appended to every technique (except output_format, which is Markdown by
# design) so the model replies in clean plain text. The front-end renders
# answers as plain text, so any Markdown syntax would otherwise show up as
# literal characters (**, #, backticks, etc.).
PLAIN_TEXT_SUFFIX = (
    " Respond in plain text only. Do not use any Markdown formatting: no "
    "asterisks for bold or italics, no backticks or code fences, no '#' "
    "headings, and no markdown bullet characters. Write in ordinary "
    "sentences and paragraphs (plain numbered or dashed lists are fine)."
)


def build_system_prompt(technique: str, custom_text: str = "") -> str:
    """Return the system prompt string for the chosen technique.

    A plain-text directive is appended to every technique except
    output_format (which intentionally produces Markdown).
    """
    prompt = _base_system_prompt(technique, custom_text)
    if technique != "output_format":
        prompt += PLAIN_TEXT_SUFFIX
    return prompt


def _base_system_prompt(technique: str, custom_text: str = "") -> str:
    """Return the raw system prompt for the chosen technique."""

    if technique == "zero_shot":
        # No examples, no persona — just a direct instruction. This is the
        # baseline that every other technique is compared against.
        return (
            "You are a helpful assistant. Answer the user's question directly "
            "and accurately."
        )

    if technique == "role":
        # Role / persona prompting: giving the model an identity tends to make
        # answers more focused and domain-appropriate.
        return (
            "You are a seasoned subject-matter expert and patient teacher. "
            "Draw on deep domain knowledge, use precise terminology, and "
            "explain your reasoning the way an experienced professional would "
            "when mentoring someone."
        )

    if technique == "few_shot":
        # Few-shot prompting: showing a couple of example Q&A pairs teaches the
        # model the desired tone and structure by imitation.
        return (
            "You are a helpful assistant. Follow the style and structure shown "
            "in the examples below when answering new questions.\n\n"
            "Example 1\n"
            "Q: What is photosynthesis?\n"
            "A: Photosynthesis is how plants turn sunlight, water, and carbon "
            "dioxide into energy (glucose) and oxygen. In short: sunlight in, "
            "food and oxygen out.\n\n"
            "Example 2\n"
            "Q: What is gravity?\n"
            "A: Gravity is the force that pulls objects with mass toward each "
            "other. It's why things fall down and why planets orbit the sun. "
            "In short: mass attracts mass.\n\n"
            "Now answer the user's question in the same concise 'plain "
            "explanation + 'In short:' summary' style."
        )

    if technique == "output_format":
        # Output-format prompting: constrain the shape of the answer so it is
        # predictable and easy to parse or scan.
        return (
            "You are a helpful assistant. Always respond using exactly this "
            "Markdown format:\n\n"
            "**Summary:** <one sentence answer>\n\n"
            "**Key points:**\n"
            "- <point 1>\n"
            "- <point 2>\n"
            "- <point 3>\n\n"
            "**Example:** <a short concrete example>\n\n"
            "Do not add anything outside this structure."
        )

    if technique == "step_by_step":
        # Chain-of-thought style: ask for explicit reasoning steps before the
        # final answer. Helps with math, logic, and multi-part questions.
        return (
            "You are a helpful assistant that explains its thinking. Break the "
            "problem down and reason through it one step at a time, numbering "
            "each step. After the steps, give a clearly labeled 'Final "
            "answer:' line that states the conclusion concisely."
        )

    if technique == "custom":
        # User-supplied system prompt. Fall back to a sensible default if the
        # box was left empty.
        return custom_text.strip() or "You are a helpful assistant."

    # Unknown technique id -> safe default.
    return "You are a helpful assistant."
