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

(Please note that Jython does not distribute the [servlet classes][]
in the installed version of Jython. You will need to ensure this
functionality is available during installs on your `CLASSPATH`. Of
course when you run your clamped jar in a container like Jetty, these
classes are available.)

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

Now that you have the pieces, pack up the war file by some means. This
next step assumes everything is in the warpack directory, with the
appropriate layout, and uses the jar command to construct the war
file:

````bash
$ jar cf hellowsgi.war -C warpack .
````

Next we will run a container to serve up this war file. I have found
[Jetty Runner][] to be the easiest way to serve a war file from the
command line:

````bash
$ java -jar jetty-runner.jar hellowsgi.war
````

You can then try out performance with Apache Benchmark:

````bash
$ ab -k -c 20 -n 50000 localhost:8080/hello/world
````

Here are the results I'm getting:

````
$ ab -k -c 20 -n 50000 localhost:8080/hello/world
This is ApacheBench, Version 2.3 <$Revision: 1554214 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        Jetty(9.1.2.v20140210)
Server Hostname:        localhost
Server Port:            8080

Document Path:          /hello/world
Document Length:        19 bytes

Concurrency Level:      20
Time taken for tests:   20.626 seconds
Complete requests:      50000
Failed requests:        0
Keep-Alive requests:    50000
Total transferred:      7700000 bytes
HTML transferred:       950000 bytes
Requests per second:    2424.18 [#/sec] (mean)
Time per request:       8.250 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)
Transfer rate:          364.57 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       1
Processing:     1    8 135.3      2    6774
Waiting:        1    8 135.3      2    6774
Total:          1    8 135.3      2    6774

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      3
  75%      3
  80%      4
  90%     13
  95%     27
  98%     46
  99%     63
 100%   6774 (longest request)
````

Note that the first requests will see initialization of the Jython runtime; then the requests will see JIT warmup. You can see this in a subsequent run of the ab tool:

````
Percentage of the requests served within a certain time (ms)
  50%      1
  66%      1
  75%      2
  80%      2
  90%      2
  95%      4
  98%      6
  99%      9
 100%    131 (longest request)
 ````

and then with a third run, the JIT really has started to see warmup:

````
Percentage of the requests served within a certain time (ms)
  50%      1
  66%      2
  75%      2
  80%      2
  90%      2
  95%      3
  98%      3
  99%      4
 100%     11 (longest request)
````

At some future point you might see the effects of a GC (confirmed by looking at JConsole as well). Just using the defaults in Java 7 on OS X 10.10.2, it's still quite reasonable:

````
Percentage of the requests served within a certain time (ms)
  50%      1
  66%      2
  75%      2
  80%      2
  90%      2
  95%      3
  98%      4
  99%      5
 100%    114 (longest request)
````

So there you go. HelloWSGI doesn't do very much, but it does
illustrate what it takes to link a standard Python WSGI app into
Jython in a very simple fashion.

<!-- references -->

[Bottle]: https://github.com/bottlepy/bottle
[Clamp]: https://github.com/jythontools/clamp
[Fireside]: https://github.com/jythontools/fireside
[Jetty Runner]: http://wiki.eclipse.org/Jetty/Howto/Using_Jetty_Runner
[Jython website]: http://www.jython.org/
[Mako]: http://www.makotemplates.org/
[pyenv]: https://github.com/yyuu/pyenv
[servlet classes]: http://docs.oracle.com/javaee/7/api/javax/servlet/package-summary.html
