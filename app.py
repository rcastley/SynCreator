"""Application entry point for development."""
from flaskr import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=8080, debug=True)
