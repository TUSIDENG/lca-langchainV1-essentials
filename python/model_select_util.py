import ipywidgets as widgets
from IPython.display import display, clear_output
import os
from dotenv import load_dotenv # Import load_dotenv

class ModelSelectUtil:
    model_configs = {
    "OpenAI": [
        ("gpt-4o", "openai"),
        ("gpt-3.5-turbo", "openai"),
        ("gpt-5-nano", "openai")
    ],
    "Deepseek": [
        ("deepseek-chat", "deepseek"),
        ("deepseek-coder", "deepseek")
    ],
    "Gemini": [
        ("gemini-pro", "gemini"),
        ("gemini-flash", "gemini")
    ],
    "Anthropic": [
        ("claude-3-sonnet-20240229", "anthropic"),
        ("claude-2.1", "anthropic")
    ]
}

    api_key_map = {
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }

    def __init__(self):
        # Load environment variables from .env file if it exists
        # Use find_dotenv=True to search for .env in parent directories, 
        # but since we are in python/ and .env is in the root, we assume it's loaded correctly.
        # Explicitly loading from the current directory (d:/code/lca-langchainV1-essentials)
        # is usually safer in notebook environments.
        load_dotenv(override=True) 
        
        self.platform_dropdown = None
        self.model_dropdown = None
        self.selected_platform = None
        self.selected_model = None
        self.platform_output = widgets.Output()
        self.model_output = widgets.Output()

    def _check_api_key_exists(self, platform_key: str) -> bool:
        env_var = self.api_key_map.get(platform_key)
        if env_var:
            # Check if the environment variable is set and not empty
            return bool(os.getenv(env_var))
        return False

    def select_platform_widget(self):
        # 1. Determine available platforms
        available_platforms = []
        for platform_name, configs in self.model_configs.items():
            # platform_key is the second element of the first tuple in configs
            # We assume all models in a platform share the same platform_key
            platform_key = configs[0][1]
            if self._check_api_key_exists(platform_key):
                available_platforms.append(platform_name)

        if not available_platforms:
            with self.platform_output:
                clear_output(wait=True)
                print("No API keys found for any configured platform. Please check your .env file.")
            return self.platform_output

        # 2. Create dropdown widget
        self.platform_dropdown = widgets.Dropdown(
            options=available_platforms,
            value=available_platforms[0],
            description='Platform:',
            disabled=False,
        )
        self.selected_platform = available_platforms[0]

        # 3. Define observer
        def on_platform_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                self.selected_platform = change['new']
                self.select_model_widget() # Update model selection when platform changes

        self.platform_dropdown.observe(on_platform_change)

        # 4. Display widget
        with self.platform_output:
            clear_output(wait=True)
            display(self.platform_dropdown)

        return self.platform_output

    def select_model_widget(self):
        if not self.selected_platform:
            return self.model_output

        # 1. Get models for the selected platform
        model_options = [model_name for model_name, _ in self.model_configs.get(self.selected_platform, [])]

        if not model_options:
            with self.model_output:
                clear_output(wait=True)
                print(f"No models configured for {self.selected_platform}.")
            return self.model_output

        # 2. Create dropdown widget
        self.model_dropdown = widgets.Dropdown(
            options=model_options,
            value=model_options[0],
            description='Model:',
            disabled=False,
        )
        self.selected_model = model_options[0]

        # 3. Define observer
        def on_model_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                self.selected_model = change['new']

        self.model_dropdown.observe(on_model_change)

        # 4. Display widget
        with self.model_output:
            clear_output(wait=True)
            display(self.model_dropdown)

        return self.model_output

    def get_selected_platform(self) -> str | None:
        """Returns the currently selected platform name."""
        return self.selected_platform

    def get_selected_model(self) -> str | None:
        """Returns the currently selected model name."""
        return self.selected_model

    def get_model_params(self) -> str | None:
        """Returns the selected model parameters in the format 'platform_key:model_name'."""
        if not self.selected_platform or not self.selected_model:
            return None
        
        # Find the platform key corresponding to the selected model
        for model_name, platform_key in self.model_configs.get(self.selected_platform, []):
            if model_name == self.selected_model:
                return f"{platform_key}:{model_name}"
        
        return None

    def display_widgets(self):
        """Convenience method to display both widgets and initialize model selection."""
        platform_widget = self.select_platform_widget()
        if platform_widget:
            # Initialize model selection based on the default platform
            self.select_model_widget()
            display(widgets.VBox([platform_widget, self.model_output]))
