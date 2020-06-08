from flask import Flask

app = Flask(__name__)

@app.route('/cur')
def hello_world():
    """Print 'Hello, world!' as the response body."""
    return 'Hello, world!'

# running the server
app.run(debug = True) # to allow for debugging and auto-reload