from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "a really really really really long secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mysqlite.db"

from views import *

if __name__ == "__main__":
    app.run(debug=True)