from pymongo import MongoClient
client = MongoClient("localhost", 27017) # votre instance mongoDB
db = client["WouawLaDb"] #le nom de votre db
collection = db["Books"] # le nom de votre collection books ( la casse est importante )
template = "templates" # remplacer par clean_templates si vous voulez des pages lisibles ( le code est plus facile à lire aussi )