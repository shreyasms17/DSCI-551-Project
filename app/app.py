from flask import Flask
import routes

app = Flask(__name__)

# Initialize routes
routes.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
