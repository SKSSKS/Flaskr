from flaskr import create_app, db, cli
from dotenv import load_dotenv
load_dotenv()

app = create_app()
cli.register(app)
