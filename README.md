HelloWSGI
=========

The HelloWSGI sample project demonstrates how to use [Fireside][] to
support running Python WSGI apps in a standard Java servlet
container. It uses the [Clamp][] project to produce a single jar for
inclusion in a war file. However, in the future it should be also
possible to support warless deployments with containers like Jetty.

Start by installing Jython 2.7. Unless you're running on Windows, the
most recent beta 4 will work for you. Get it at the
[Jython website][]. You will want to bootstrap pip (this next step
will be part of the Jython installer by the final release):

````bash
$ jython -m ensurepip
````

With this step, the pip command is now available in
`$JYTHON_HOME/bin`. You may want to alias `$JYTHON_HOME/bin/pip` as
`jpip`, or you can use [pyenv][] to manage working with CPython's pip.

Next install the HelloWSGI depdendencies. Clamp and Fireside are
essential, whereas you can use the WSGI-compliant tooling of your
choice; I have simply chosen [Bottle][] and [Mako][] as being
particularly simple. Using Jython's pip:

````bash
pip install bottle mako
pip install git+https://github.com/jythontools/clamp.git
pip install git+https://github.com/jythontools/fireside.git
````

Now you can build an über jar for HelloWSGI by running the install and
singlejar build steps:

````bash
$ jython setup.py install singlejar
````

This setup will result in `hellowsgi-0.1-single.jar`. (The version, such
as 0.1, comes from `setup.py`.) With the jar built, we put it in a war
file with the usual layout:

````
.
├── META-INF
│   └── MANIFEST.MF
└── WEB-INF
    ├── lib
    │   └── hellowsgi-0.1-single.jar
    └── web.xml
````

Configure `web.xml` for the war file something like this, adding other
servlets as desired, not to mention other configuration. The key piece
is the entry point for Fireside is specified by `wsgi.handler`; simply
point it to a callable supporting the WSGI standard.

````xml
<web-app xmlns="http://java.sun.com/xml/ns/javaee"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_3_0.xsd"
      version="3.0">  
        
  <servlet>
   <servlet-name>fireside</servlet-name>
   <servlet-class>org.python.tools.fireside.servlet.WSGIServlet</servlet-class>
   <init-param>
     <param-name>wsgi.handler</param-name>
     <param-value>hellowsgi.simple_app</param-value>
   </init-param>
  </servlet>

  <servlet-mapping>
    <servlet-name>fireside</servlet-name>
    <url-pattern>/*</url-pattern>
  </servlet-mapping>
</web-app>
````

It's pretty easy to do just that, especially with something like
Bottle. If you look at the HelloWSGI sample code, the
`hellowsgi.simple_app` entry point and corresponding code is defined
as follows:

````python
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
````

Now that you have the pieces, pack up the war file by some
means. Assuming everything is in the warpack directory, The jar
command can be used for this:

````bash
$ jar cf hellowsgi.war -C warpack .
````

Next, [Jetty Runner][] is the easiest way to serve a war file from the
command line:

````bash
$ java -jar jetty-runner.jar hellowsgi.war
````

You can then try out performance with Apache Benchmark:

````bash
$ ab -k -c 20 -n 50000 localhost:8080/hello/world
````

<!-- references -->

[Bottle]: https://github.com/bottlepy/bottle
[Clamp]: https://github.com/jythontools/clamp
[Fireside]: https://github.com/jythontools/fireside
[Jetty Runner]: http://wiki.eclipse.org/Jetty/Howto/Using_Jetty_Runner
[Jython website]: http://www.jython.org/
[Mako]: http://www.makotemplates.org/
[pyenv]: https://github.com/yyuu/pyenv
