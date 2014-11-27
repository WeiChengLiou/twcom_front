#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from pymongo import MongoClient
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.contrib.fixers import ProxyFix # for gunicorn
import json
import re
import requests
from urllib import unquote

db = None
col = None

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app) # for gunicorn

def getidlike(query):
    res = requests.get("http://dataing.pw/query?com=%s" % query)
    if res!="null":
        return json.loads(res.json())

def getbosslike(query):
    res = requests.get("http://dataing.pw/query?boss=%s" % query)
    if res!="null":
        return json.loads(res.json())

def to_node(d):
    return {"id": d["id"],
            "name": d["name"],
            "market": d["market"] }

@app.route("/")
def mainpage():
    print "main page"
    return render_template('index.html')


# --- search function ---
@app.route("/search", methods=['POST'])
def search_companynet():
    print "in search"
    option = query = ''

    if request.method == 'POST':
        
        try:
            option = request.form['searchopt']
            query = request.form['query']
            graph = request.form['graphopt']
            print "/search/"+query

        except:
            return "Error: unable to get the form"
        
        if option == "company":
            # search by company id
            if re.match("^[\d]{8}$", query)!=None:
                return redirect("%s/id/%s" % (graph, query))

            # search by company name
            results = getidlike(query)
            q = u"公司名稱 %s" % query

            if len(results) == 1:
                return redirect("%s/id/%s" % (graph, results.keys()[0]))
            print "graph=%s" % graph 
            return render_template('list.html', graph=graph, query=q, targets=results, querytype='id')
            #ids = results.keys()
            #if len(ids) > 1:
            #    print "redirect to /company/id/%s" % ids[0]
            #    return redirect("company/id/%s" % ids[0])
            #else:
            #    return "Company not found!"

        elif option == "boss":
            results = getbosslike(query)
            print results
            q = u"董事長姓名 %s" % query
            return render_template('list.html', graph=graph, query=q, targets=results, querytype='boss')
            #return redirect("company/boss/%s" % query)


    else:
        return redirect("/")

# --- for Cross-Origin Resources Sharing ---
@app.route("/getjson", methods=['GET'])
def getJson():
    print "in getjson" 
    if 'api' in request.args:
        url = request.args['api']
        print url
        print unquote(url)

        data = requests.get(unquote(url))
        if data.status_code != 200:
            return json.dumps({ "error" : "REST API error - %s" % data.status_code})
        else: 
            return data.json()
    else:
        return json.dumps({ "error" : "GET argument error - %s"})
#    G = get_network(cid, maxlvl=1)
#    if G:
#        return exp_company(G, "%s.cache" % cid)

# --- internal APIs ---
@app.route("/company/id/<cid>", methods=['GET'])
def show_company_byid(cid):
    print 'company/id/%s' % cid
    maxlvl = '1'
    if 'maxlvl' in request.args:
        maxlvl = request.args['maxlvl']
    
    print 'test'
    url = "http://dataing.pw/com?id=%s&maxlvl=%s" % (cid, maxlvl)
    q = u"公司編號 %s" % cid
    info = u"公司關係圖"
    return render_template('graph.html', query=q, url=url, graphinfo=info)


@app.route("/company/boss/<boss>")
def show_company_byboss(boss):
    if 'maxlvl' in request.args:
        maxlvl = request.args['maxlvl']
    else:
        maxlvl = '1'
    url = "http://dataing.pw/com?boss=%s&maxlvl=%s" % (boss, maxlvl)
    q = u"董事長姓名 %s" % boss
    info = u"公司關係圖"
    return render_template('graph.html', query=q, url=url, graphinfo=info)


@app.route("/companyaddr/id/<cid>")
def show_addrnet_byid(cid):
    if 'maxlvl' in request.args:
        maxlvl = request.args['maxlvl']
    else:
        maxlvl = '1'
    url = "http://dataing.pw/com?comaddr=%s&maxlvl=%s" % (cid, maxlvl)
    q = u"公司編號 %s" % cid
    info = u"公司關係圖-同地址之公司"
    return render_template('graph.html', query=q, url=url, graphinfo=info)

@app.route("/companyboard/id/<cid>")
def show_boardnet_byboard(cid):
    if 'maxlvl' in request.args:
        maxlvl = request.args['maxlvl']
    else:
        maxlvl = '1'
    url = "http://dataing.pw/com?comboss=%s&maxlvl=%s" % (cid, maxlvl)
    q = u"公司編號 %s" % cid
    info = u"公司關係圖-子母公司及共同董事關係"
    return render_template('graph.html', query=q, url=url, graphinfo=info)


@app.route("/board/id/<cid>")
def show_boardnet_byid(cid):
    if 'maxlvl' in request.args:
        maxlvl = request.args['maxlvl']
    else:
        maxlvl = '1'
    url = "http://dataing.pw/boss?id=%s&maxlvl=%s" %(cid, maxlvl)
    q = u"公司編號 %s" % cid
    info = u"公司董事關係圖"
    return render_template('graph.html', query=q, url=url, graphinfo=info)

