def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    output = b'Hello World. Calling in via Fireside!\n'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [output]
