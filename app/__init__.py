from flask import Flask, render_template
from livereload import Server

def create_app():
    app = Flask(__name__)

    app.config.update(
        TESTING=True,
        TEMPLATES_AUTO_RELOAD=True,
    )
    @app.route('/hello')
    def hello():
        return "Hello World!"

    # @app.errorhandler(404)
    # def page_not_foud(error):
    #     return render_template(url_for('page_not_found.html')), 404
        
    @app.route('/index')
    def index():
        return render_template('index.html', token="hello react")

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from . import tx_list
    app.register_blueprint(tx_list.bp)
   
    @app.route('/template')
    def template():
        return render_template('index.html')


    return app
if __name__=='__main__':
    app = create_app()
    server = Server(app.wsgi_app)
    server.watch('**/*.*')
    server.server()
    # app.run()
