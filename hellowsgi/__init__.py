from bottle import Bottle, MakoTemplate, route

simple_app = app = Bottle()
hello_template = MakoTemplate('<b>Hello ${name}</b>!')
bye_template = MakoTemplate('<b>Bye ${name}</b>!')


@app.route('/hello/<name>')
def index(name):
    return hello_template.render(name=name)

@app.route('/bye/<name>')
def index(name):
    return bye_template.render(name=name)


