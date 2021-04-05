from flask import Flask, render_template
from flask.helpers import url_for

def create_app():
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return "Hello World!"

    # @app.errorhandler(404)
    # def page_not_foud(error):
    #     return render_template(url_for('page_not_found.html')), 404
        
    @app.route('/')
    def index():
        return render_template('base.html')
    return app

if __name__=='__main__':
    app = create_app()
    app.run()
