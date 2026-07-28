from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager

mysql = MySQL()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.secret_key = 'invoice@app#2026$secret'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '7283566@Op'
    app.config['MYSQL_DB'] = 'invoice_db'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.clients import clients
    from app.routes.invoices import invoices
    from app.routes.products import products
    from app.routes.settings import settings

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(clients)
    app.register_blueprint(invoices)
    app.register_blueprint(products)
    app.register_blueprint(settings)

    @app.context_processor
    def inject_currency():
        from flask_login import current_user
        if current_user.is_authenticated:
            return {'currency': current_user.currency}
        return {'currency': '$'}

    return app
