import os
#Factory
from flask import Flask


def create_app(test_config=None): #App factory function.
    # create and configure the app
    #    current Python module
    app = Flask(__name__, instance_relative_config=True) #Creates flask instant.
    #                   files are relative to instance folder
    app.config.from_mapping( #default configurations
        SECRET_KEY='dev', #Used by flask to keep data safe.
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        #Path that flask has choosen for the instance folder.
    )

    if test_config is None: #Different configurations that overrides default and are used as tesing.
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) #Overrides defaults and takes configurations from config.py
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config) #Overrides defaults are passed down as the configurations.
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)#Ensures app.instance_path exists. Where SQLite database file will be created.
    except OSError:
        pass
    # a simple page that says hello, use to test the url.
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #Import and call db
    from . import db
    db.init_app(app) #init-db has been registered with the app

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/',endpoint='index')

    return app
