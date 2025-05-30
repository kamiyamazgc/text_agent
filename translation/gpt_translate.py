import os, textwrap, tiktoken, openai

class GPT4OMiniTranslator:
    """
    English ➜ Japanese translator using the OpenAI ChatCompletion API.
    • model:  'gpt-4o-mini'  (or 'gpt-4.1-mini')
    • needs   OPENAI_API_KEY  env var or api_key kwarg
    """

    def __init__(self, api_key=None, model="gpt-4o-mini", max_ctx=120_000):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model  = model
        # Use a fixed encoding for tokenization
        self.enc    = tiktoken.get_encoding("cl100k_base")
        # leave ~8 k tokens headroom for the reply + prompt tokens
        self.max_in = max_ctx

        self.system_prompt = (
            "You are a professional human translator. "
            "Translate the user's English text into natural, polite Japanese. "
            "Return ONLY the Japanese translation."
        )

    # ---------- helpers -----------------------------------------------------
    def _split(self, text: str):
        ids = self.enc.encode(text)
        for i in range(0, len(ids), self.max_in):
            yield self.enc.decode(ids[i:i + self.max_in])

    # ---------- public ------------------------------------------------------
    def translate(self, text: str) -> str:
        out = []
        for i, chunk in enumerate(self._split(text), 1):
            print(f"⟳ OpenAI chunk {i}", end="\r")
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user",   "content": chunk},
                ],
            }
            if self.model != "o4-mini":
                kwargs["temperature"] = 0.2
                kwargs["top_p"] = 0.9
            resp = self.client.chat.completions.create(**kwargs)
            out.append(resp.choices[0].message.content.strip())
        print("✓ done")
        return "\n".join(out)
