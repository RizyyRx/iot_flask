from flask import Flask, redirect, url_for, request, render_template
import os
import math


app = Flask(__name__) #app is an object being created of class Flask
basename = '/iot' #use a base dir if needed and add it to app route

@app.route(basename+'/') #decorator that binds url with a function
def hello_world():
   d={"username": whoami().strip(),"env": "wsl_kali"}
   return render_template('helloworld.html',data=d)

#runs whoami linux cmd and displays output (note that the output contains \n at the end of the string)
@app.route(basename+'/whoami')
def whoami():
   return os.popen('whoami').read()

# outputs cpu info
@app.route(basename+'/cpuinfo')
def cpu_info():
   if isadmin() == "yes":
      # redirects to error() with errorcode parameter as 1000 if user is admin 
      #redirect() can be used to redirect user to any url (gives 302 response to a request..)
      #url_for() is used to generate a url for the specified function
      return redirect(url_for('error',errorcode=1000)) # instead of url_for, using "basename+'/error/1000'" will also work
   else:
      return "<pre>" + os.popen('cat /proc/cpuinfo').read() + "</pre>"

# using <test> like parameter in the decorator url will act as a parameter to the function
#this just echoes the string what we give in the url
@app.route(basename+'/echo/<string>')
def echo(string):
    return string

#specific data types such as int, float can be retrieved by url using int: or float: in the rule parameter
@app.route(basename+'/power/<int:a>/<int:b>') 
def power(a,b):
    return "power of {} to {} is {}".format(a,b,math.pow(a,b))

#in this path type, whole path can be given as input thru url
@app.route(basename+'/path/<path:p>')
def path(p):
   return p

#checks if user is admin or not (uses whoami() func)
@app.route(basename+'/isadmin')
def isadmin():
   if whoami() == "root\n":
      return "yes"
   else:
      return "no"

#displays error messages according to errorcodes
@app.route(basename+'/error/<int:errorcode>')
def error(errorcode):
   if errorcode == 1000:
     return "you are running this as root, which is not recommended"
   elif errorcode == 1001:
     return "some error...."
   else:
      return "unknown error"

@app.route(basename+'/sqrt',methods=['GET','POST'])
def sqrt():
   return{ 
      "result": str(math.sqrt(int(request.form['num'])))
   }

if __name__ == '__main__': #name == main checks that if this is the main file or not
   app.run(debug=True)