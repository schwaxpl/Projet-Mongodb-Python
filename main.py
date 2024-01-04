
from flask import Flask, render_template, redirect,request
from books import *
from graphs_bokeh import *
import config
app = Flask(__name__,template_folder=config.template)

db = config.db
books = config.collection

def createTask(form):
    
    type = form.type.data
    titre = form.titre.data
    annee = form.year.data
    str_auteurs = form.auteurs.data
    tab_auteurs = str_auteurs.split(",")
    auteurs = []
    for a in tab_auteurs:
        auteurs.append(a)

    id = str(annee) + "/" + type + "/" + titre 
    
    book = {'_id':id, 'title':titre, 'type':type, 'year':annee,"authors":auteurs}

    books.insert_one(book)
    print("CREATE")
    #return redirect('/')

def deleteTask(form):
    key = form.key.data
    auteur = form.auteur.data
    annee = form.annee.data
    tab_auteurs = auteur.split(",")
    auteurs = []
    for a in tab_auteurs:
        auteurs.append(a)

    deleteQuery = {}
    if(key):
        deleteQuery["_id"] = key
    if(auteur):
        deleteQuery["authors"] = {"$all":auteurs}
    if(annee):
        deleteQuery["year"] = annee
    if(deleteQuery != {}):
        books.delete_many(deleteQuery)

    #return redirect('/')

def updateTask(form):
    key = form.key.data
    titre = form.titre.data
    annee = form.annee.data
    updateQuery = {}
    if(titre != ""):
        updateQuery["title"] = titre
    if(annee != None):
        updateQuery["year"] = annee

    if(updateQuery!={}):
        books.update_one(
            {"_id": key},
            {"$set":
                updateQuery
            }
        )


@app.route('/', methods=['GET','POST'])
def main():
    limit = 10
    # create form
    cform = CreateTask(prefix='cform')
    dform = DeleteTask(prefix='dform')
    uform = UpdateTask(prefix='uform')
    sform = SearchTask(prefix='sform')
    reset = ResetTask(prefix='reset')

    # response
    if cform.validate_on_submit() and cform.create.data:
        createTask(cform)
    if dform.validate_on_submit() and dform.delete.data:
        deleteTask(dform)
    if uform.validate_on_submit() and uform.update.data:
        return updateTask(uform)
        
    
    #On initialise les filtres
    filter =[]
    matchFilter ={}

    #Si j'ai soumis la recherche j'ajoute mes filtres dans mon dictionnaire
    if sform.validate_on_submit() and sform.search.data:
        if sform.auteur.data !="":
            matchFilter["authors"] = {"$regex":'.*'+sform.auteur.data+'.*',"$options":"i"}
        if sform.titre!="":
            matchFilter["title"] = {"$regex":'.*'+sform.titre.data+'.*',"$options":"i"}
        annee = sform.annee.data
        if annee != None:
            matchFilter["year"] = {"$eq":sform.annee.data}
        if sform.type.data!="":
            matchFilter["type"] = {"$regex":".*"+sform.type.data+".*","$options":"i"}
        limit = int(sform.nb_resultats.data)

    filter.append({"$match":matchFilter})

    #Orientation du tri avec le sens
    sens_tri = -1 if sform.sens_tri.data == "Décroissant" else 1

    #Quel paramètre pour le tri
    if(sform.tri.data == "annee"):
        filter.append({"$sort":{"year":sens_tri}})
    elif(sform.tri.data== "titre"):
        filter.append({"$sort":{"title":sens_tri}})

    skip = 0
    if(sform.page_debut and sform.page_debut.data>1):
        skip = (sform.page_debut.data-1)*limit
        filter.append({"$skip":skip})
    debut = 1 + skip
    nb_total = books.count_documents(matchFilter)

    filter.append({"$limit":limit})
    docs = books.aggregate(filter)
    
    data = []
    for i in docs:
        data.append(i)
    nb_limite = len(data)
    fin = debut + nb_limite-1
    if fin<debut:
        debut = "Aucun livre"
        fin = " afficher (page non existante)"
    return render_template('home.html', cform = cform, dform = dform, uform = uform, \
            data = data, reset = reset,sform = sform, nb_total = nb_total, nb_limite = nb_limite, debut = debut, fin = fin)

@app.route('/stats', methods=['GET','POST'])
def stats():

   
    top_10_auteurs = books.aggregate([{ "$unwind": { "path": '$authors' } },
    {
      "$group": {
        "_id": '$authors',
        "nbWritten": { "$sum": 1 }
      }
    },
    { "$sort": { "nbWritten": -1 } },
    {"$limit":10}
  ])
    cpt = 1
    auteurs = list(top_10_auteurs)
    auteurs_html = ""
    for a in auteurs:
        auteurs_html += "<div class='sub'><b style='color:red;font-size:12px;'>"+str(cpt)+" - </b><b>"+a["_id"]+"</b> : "+str(a["nbWritten"])+"<br/></div>"
        cpt+=1
    auteurs_html +=""

    top_10_articles = books.aggregate([
    {
      "$match": {
        "type": 'Article',
        "pages": { "$exists": "true" }
      }
    },
    {
      "$project": {
        "_id":1,
        "title": 1,
        "authors": 1,
        "nb_pages": {
          "$subtract": [
            '$pages.end',
            '$pages.start'
          ]
        }
      }
    },
    { "$sort": { "nb_pages": -1 } },
    {"$limit":10}
    ])
    articles = list(top_10_articles)
    cpt = 1
    articles_html = ""
    for a in articles:
        print(a["title"] + str(a["nb_pages"]))
        articles_html += "<div class='sub'><b style='color:red;font-size:12px;'>"+str(cpt)+" - </b><b>"+a["_id"]+"</b> : "+str(a["nb_pages"])+"<br/></div>"
        cpt+=1
    articles_html +=""
    stats_jolies = {}

    stats_jolies["Top 10 des articles les plus longs"] = articles_html
    stats_jolies["Top 10 des auteurs"] = auteurs_html
    return render_template('stats.html', stats= stats_jolies)

@app.route('/infos', methods=['GET','POST'])
def infos():

    books_infos = db.command("collstats", "Books")
    books_stats_jolies = {}
    for k,d in books_infos.items():
        books_stats_jolies[k] = str(d)[:100] +"..." if len(str(d))>100 else str(d)

    base_infos = db.command("dbstats")
    base_stats_jolies = {}
    for k,d in base_infos.items():
        base_stats_jolies[k] = str(d)[:100] +"..." if len(str(d))>100 else str(d)


    return render_template('infos.html', stats= books_stats_jolies, base_stats = base_stats_jolies)


@app.route('/graphs', methods=['GET','POST'])
def graphs():


    ga = graph_annees(books)
        # Get Chart Components 
    script, div = components(ga) 
    gt = graph_types(books)
        # Get Chart Components 
    script_types, div_types = components(gt) 
  
    return render_template('graphs.html', script=script, 
        div=div,div_types =div_types,script_types=script_types)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key' # your app key
    app.debug = True # set to true if you want to enable debug
    app.run(host='0.0.0.0', port=8000) # change port according to your needs
