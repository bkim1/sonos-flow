import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flow.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load env variables
    from dotenv import load_dotenv
    load_dotenv()
    # from pathlib import Path  # python3 only
    # env_path = Path('.') / 'vars.env'
    # load_dotenv(dotenv_path=env_path)
    
    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    # register the other blueprints to the app
    from app import auth, flow_control
    app.register_blueprint(auth.bp)
    app.register_blueprint(flow_control.bp)


    return app