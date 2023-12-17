import os
from pathlib import Path


def main():
    """
    Run Streamlit app
    """
    current_dir = Path(__file__).parent.resolve()
    app_filepath = current_dir / "src" / "🏠_Homepage.py"

    os.system(f"streamlit run \"{app_filepath}\"")


if __name__ == "__main__":
    main()
