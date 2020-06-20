#coding=utf-8
from flask import Flask, jsonify, render_template,request,redirect,url_for,session
from py2neo import Graph
from werkzeug.utils import secure_filename
import os
#


from getNewSample import getNewSample

#
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
graph = Graph(host=("localhost"),port=("7687"),auth=("neo4j","nmj@12345"))


def buildNodes(nodeRecord):
    #data = {"id":nodeRecord.n._id, "label": next(iter(nodeRecord.n._labels))}
    #data.update(nodeRecord.n.properties)
    sem=str(nodeRecord.get('n'))
    semm=sem.split('md5: \'')[1]
    semmm=semm.split('\'')[0]
    a=sem.split('{')
    typee=sem.split('type')[1][3:6]
    print(typee)
    b=a[1][:-2]
    c=b.split('\'')
    ddd=c[1].encode('utf-8').decode("unicode_escape")
    data = { "id": nodeRecord.get('n').identity,"label":c[1],"title":b,"size":2,"name":ddd,'ttype':typee,'mdd':semmm}

    #data = {"id": str(nodeRecord.get('n').get('id')),"label": str(nodeRecord.get('n').get('label'))}
    return data

def buildEdges(relationRecord):

    stt=str(relationRecord['r'].start_node).split('{')[1].split(',')[0].split(':')[1][2:-1]
    ett=str(relationRecord['r'].end_node).split('{')[1].split(',')[0].split(':')[1][2:-1]
    ppp=(str(relationRecord['r']).split('{'))[1]
    ppp1=(ppp.split('}'))[0]
    ppp2=(ppp1.split(':'))[1]
    ppp3=int(ppp2[1:])/300
    if stt==ett:
        ppp3=0.01
    data = {'source': str(relationRecord['r'].start_node.identity), 
            'target': str(relationRecord['r'].end_node.identity),
            'width':ppp3,
            'sname':stt,
            'tname':ett
            #"relationship": relationRecord.type}
            #"relationship": str('use')}
    }
    return data

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/bg')
def bg():
    return render_template('bg.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/')
def dash():
    return render_template('dash.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/introduction')
def introduction():
    return render_template('introduction.html')

@app.route('/output')
def output():
    return render_template('output.html')

@app.route('/output1')
def output1():
    recvv=getNewSample(session.get('username'),'True')
    recvvv=str(recvv).split(':')
    if (recvvv[0][2:-1]=='err'):
        rett={}
        rett[0]=1
        rett[1]=recvvv[1][2:-2]
        print("#",rett)
        return rett
    elif (recvvv[1][1]=="n"):
        print("@")
        return "this is not apt"
    recvvvv=str(recvv).split(",")
    return recvv['classify']

@app.route('/graph')
def get_graph():
    nodelists=[]
    a=graph.run('MATCH (n :Sample) RETURN n').data()
    for i in a:
        nodelists.append(i)
    #b=graph.run('MATCH (n { family: "Mallu_Cyber_Soldiers" }) RETURN n').data()
    #for i in b:
    #    if i not in nodelists:
    #        nodelists.append(i)
  
    nodes=list(map(buildNodes,nodelists))
    print('1\n')

    edgelists=[]
    listt=[]
    #c=graph.run('MATCH (p1 { family: "Hangover" })-[r1]->(n)<-[r2]-(p2{family:"Mallu_Cyber_Soldiers"}) RETURN r1,r2').data()
    #c=graph.run('MATCH (p1{ family: "Hangover" })-[r1]->(n)<-[r2]-(p2:Sample) RETURN p1,p2').data()
    #for i in c:
    #    if ((i['p1'].identity,i['p2'].identity) not in listt)and((i['p2'].identity,i['p1'].identity) not in listt):
    #        listt.append((i['p1'].identity,i['p2'].identity))
    #        edgelists.append(i)
    c=graph.run('MATCH (a)-[r]->(b) RETURN r').data()
    for i in c:
        
        #ppp=(str(i['r']).split('{'))[1]
        #ppp1=(ppp.split('}'))[0]
        #ppp2=(ppp1.split(':'))[1]
        #if (int(ppp2[1:]))>200:
        edgelists.append(i)
    #c=graph.run('MATCH (a { family: \'MuddyWater\' })-[r]->(b) RETURN r').data()
    #for i in c:
    #    if i not in edgelists:
    #        edgelists.append(i)
    edges = list(map(buildEdges,edgelists))
    print('2\n')
    return jsonify({"nodes": nodes, "edges": edges}) 

@app.route('/graph1')
def get_graph1():
    nodelists=[]
    a=graph.run('MATCH (n :Sample) RETURN n').data()
    for i in a:
        nodelists.append(i)
    #b=graph.run('MATCH (n { family: "Mallu_Cyber_Soldiers" }) RETURN n').data()
    #for i in b:
    #    if i not in nodelists:
    #        nodelists.append(i)

    nodes=list(map(buildNodes,nodelists))
    return jsonify({"nodes":nodes})

@app.route('/graph2')
def get_graph2():
    nodelists=[]
    a=graph.run('MATCH (n :Sample) RETURN n').data()
    for i in a:
        nodelists.append(i)
    #b=graph.run('MATCH (n { family: "Mallu_Cyber_Soldiers" }) RETURN n').data()
    #for i in b:
    #    if i not in nodelists:
    #        nodelists.append(i)

    nodes=list(map(buildNodes,nodelists))
    return jsonify({"nodes":nodes})

@app.route('/graph3')
def get_graph3():
    nodelists=[]
    a=graph.run('MATCH (n :Sample) RETURN n').data()
    for i in a:
        nodelists.append(i)
    #b=graph.run('MATCH (n { family: "Mallu_Cyber_Soldiers" }) RETURN n').data()
    #for i in b:
    #    if i not in nodelists:
    #        nodelists.append(i)

    nodes=list(map(buildNodes,nodelists))
    return jsonify({"nodes":nodes})

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  
        upload_path = os.path.join(basepath,"static/uploads",secure_filename(f.filename)) 
        if ("/home/zxk/new2/webd/static/uploads/" == upload_path):
            return render_template('upload.html')
        f.save(upload_path)
        session['username']=upload_path
        return redirect(url_for('output'))
    return render_template('upload.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099,debug = True)
