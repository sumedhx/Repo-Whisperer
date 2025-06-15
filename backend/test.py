import google.generativeai as genai

GEMINI_API_KEY = 'AIzaSyCfziDjvhQ3JKkDlDnVDw0CyO679CpxD-4'
genai.configure(api_key=GEMINI_API_KEY)

def list_models():
    try:
        models = genai.list_models()
        print("Available models:")
        for model in models:   # iterate directly over the generator
            print(f"- {model.name} (supports: {model.supported_generation_methods})")
    except Exception as e:
        print(f"Error listing models: {e}")

list_models()
