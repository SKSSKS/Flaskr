import os
from flask import Flask
from flask import render_template

def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # for 404 httprequest error
    app.register_error_handler(404, page_not_found)
    
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE =  os.path.join(app.instance_path, 'flaskr.sqlite'),
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('congig.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    
    #from . import db
    db.init_app(app)
    with app.app_context():
        db.init_db()

    
    #from . import auth
    app.register_blueprint(auth.bp)

    #from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    return app

from flaskr import db, auth, blog
