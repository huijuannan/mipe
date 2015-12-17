import sae
from app.myapp import app

application = sae.create_wsgi_app(app) 