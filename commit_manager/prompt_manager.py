from typing import Optional
import tomli


class PromptManager:
    def __init__(self, toml_file_path: str) -> None:
        with open(toml_file_path, "rb") as file:
            self.prompts = tomli.load(file)

    def get_prompt(self, category: str, key: str) -> Optional[str]:
        """
        Retrieve a prompt by category and key.
        """
        return self.prompts.get(category, {}).get(key, None)
