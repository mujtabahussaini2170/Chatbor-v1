"""Optional Hugging Face Transformers response generator.

This is an extension point, not enabled by default: transformer models can be
large and may download several hundred MB the first time they are used.
Install with: pip install transformers torch
"""

def generate_with_transformer(prompt, model_name="google/flan-t5-small"):
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError("Install the optional packages: pip install transformers torch") from exc

    generator = pipeline("text2text-generation", model=model_name)
    result = generator(prompt, max_new_tokens=100, do_sample=False)
    return result[0]["generated_text"]
