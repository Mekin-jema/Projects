"""Root entry point for the Amin AI API."""

from app.main import app


def main():
    """Print the available application entrypoints."""
    print("Amin AI API is ready. Run: uvicorn main:app --reload")
    print("Streamlit UI: uv run streamlit run app/ui/streamlit_app.py")
    

if __name__ == "__main__":
    main()
