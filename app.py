from flask import Flask, jsonify, request, Response, send_file, render_template
from pathlib import Path
from markupsafe import escape
import json, sys, os
from sys import platform
from datetime import datetime
from flask_cors import CORS
import argparse

home = str(Path.home())

app = Flask(__name__)
CORS(app)

parser=argparse.ArgumentParser()

parser.add_argument("--ip", help="The ip to run the server on")
parser.add_argument("--port", help="The port of the server")
parser.add_argument("--dir", help="The folder that the server points to")

args=parser.parse_args()

if args.dir == None:
    print("No directory was provided")
    sys.exit(1)
    
if args.ip == None:
    print("No ip was provided. Defaulting to 'localhost'")

if args.port == None:
    print("No port provided. Defaulting to 8000")

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

@app.route("/img/parentdir")
def getimgparentdir():
    return send_file("./public/parentdir.png")

@app.route("/img/folder")
def getimgfolder():
    return send_file("./public/folder.png")

@app.route("/img/file")
def getimgfile():
    return send_file("./public/file.png")

@app.route("/<path:subpath>")
def getdirectory(subpath):
    directory = args.dir + subpath + "/"
    if os.path.isdir(directory):
        files_and_directories = os.listdir(directory)
        
        data = {}
        parentdir = "Parent Directory"
        data["parentdir"] = "/".join(("/" + subpath).split("/")[0:-1])
        if data["parentdir"] == "":
            data["parentdir"] = "/"
        print(data["parentdir"])
         
        for file in files_and_directories:
            data[file] = {}
            data[file]["type"] = "dir" if os.path.isdir(directory + file) else "file" 
            data[file]["sizebytes"] = "0" if os.path.isdir(directory + file) else os.path.getsize(directory + file)
            data[file]["size"] = "0" if os.path.isdir(directory + file) else sizeof_fmt(data[file]["sizebytes"])
            data[file]["modifiedunix"] = os.path.getmtime(directory + file)
            data[file]["modified"] = datetime.utcfromtimestamp(os.path.getmtime(directory + file)).strftime('%Y-%m-%d %H:%M')
            data[file]["created"] = os.path.getctime(directory + file)
            
        return render_template("index.html", data=data, subpath=subpath)
        #return data


    return Response(json.dumps("Provided path is not a directory"), status=400, mimetype='application/json')

@app.route("/")
def getrootdir():
    directory = args.dir
    files_and_directories = os.listdir(directory)
    
    data = {}
        
    for file in files_and_directories:
        data[file] = {}
        data[file]["type"] = "dir" if os.path.isdir(directory + file) else "file" 
        data[file]["sizebytes"] = os.path.getsize(directory + file)
        data[file]["size"] = sizeof_fmt(data[file]["sizebytes"])
        data[file]["modifiedunix"] = os.path.getmtime(directory + file)
        data[file]["modified"] = datetime.utcfromtimestamp(os.path.getmtime(directory + file)).strftime('%Y-%m-%d %H:%M')
        data[file]["created"] = os.path.getctime(directory + file)

    #return Response(json.dumps(data), status=200, mimetype='application/json')
    return render_template("index.html", data=data, subpath=None)

@app.route("/json/<path:subpath>")
def getdirectoryjson(subpath):
    directory = args.dir + subpath + "/"
    if os.path.isdir(directory):
        files_and_directories = os.listdir(directory)
        
        data = {}
        
        parentdir = "Parent Directory"
        data["parentdir"] = "/".join((directory).split("/")[0:-2])
         
        for file in files_and_directories:
            data[file] = {}
            data[file]["type"] = "dir" if os.path.isdir(directory + file) else "file" 
            data[file]["sizebytes"] = "0" if os.path.isdir(directory + file) else os.path.getsize(directory + file)
            data[file]["size"] = "0" if os.path.isdir(directory + file) else sizeof_fmt(data[file]["sizebytes"])
            data[file]["modifiedunix"] = os.path.getmtime(directory + file)
            data[file]["modified"] = datetime.utcfromtimestamp(os.path.getmtime(directory + file)).strftime('%Y-%m-%d %H:%M')
            data[file]["created"] = os.path.getctime(directory + file)

        return Response(json.dumps(data), status=200, mimetype='application/json')
    return Response(json.dumps("Provided path is not a directory"), status=400, mimetype='application/json')

@app.route("/json")
def getrootdirjson():
    directory = args.dir
    files_and_directories = os.listdir(directory)
    
    data = {}
        
    for file in files_and_directories:
        data[file] = {}
        data[file]["type"] = "dir" if os.path.isdir(directory + file) else "file" 
        data[file]["sizebytes"] = os.path.getsize(directory + file)
        data[file]["size"] = sizeof_fmt(data[file]["sizebytes"])
        data[file]["modifiedunix"] = os.path.getmtime(directory + file)
        data[file]["modified"] = datetime.utcfromtimestamp(os.path.getmtime(directory + file)).strftime('%Y-%m-%d %H:%M')
        data[file]["created"] = os.path.getctime(directory + file)

    return Response(json.dumps(data), status=200, mimetype='application/json')

@app.route("/download/<path:subpath>")
def downloadfile(subpath):
    directory = args.dir + subpath
    if os.path.isdir(directory):
        return Response(json.dumps("Directory is not a file"), status=400, mimetype='application/json')
    
    return send_file(directory, as_attachment=True)

@app.route("/favicon.ico")
def favicon():
    return send_file("./public/favicon.ico")

if __name__ == '__main__':
    app.run(host=args.ip if args.ip != None else "localhost", port=args.port if args.port != None else 8000, debug=False)
    
