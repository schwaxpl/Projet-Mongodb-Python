from bokeh.embed import components 
from bokeh.plotting import figure 
from bokeh.palettes import Light8 as palette
import math
def graph_annees(col):
    # Defining Chart Data 
    data = col.aggregate([{"$group": {"_id": '$year',"nbLivres": { "$sum": 1 }}},{"$sort":{"_id":1}}])

    annees = []
    nb = []
    for i in data:
        annee = i["_id"]
        annees.append(str(annee))
        nb.append(i["nbLivres"])
    # Creating Plot Figure 
    p = figure( 
        x_range=annees, 
        height=400, 
        title="Livres par années", 
        sizing_mode="stretch_width"
    ) 
    
    # Defining Plot to be a Vertical Bar Plot 
    p.vbar(x=annees, top=nb, width=0.5) 
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.xaxis.major_label_orientation = "vertical"
    
    return p

def graph_types(col):
    # Defining Chart Data 
    data = col.aggregate([{"$group": {"_id": '$type',"nbLivres": { "$sum": 1 }}},{"$sort":{"_id":1}}])

    types = []
    nb = []
    for i in data:
        type = i["_id"]
        types.append(str(type))
        nb.append(i["nbLivres"])
    # Creating Plot Figure 
    p = figure( 
        title="Livres par type"
    )

    sum = 0
    for n in nb:
        sum += n    
    
    pourcent = []
    for n in nb:
        pourcent.append( n/sum)
    
    radians = [math.radians((per)*360) for per in pourcent]
    # starting angle values 
    start_angle = [math.radians(0)] 
    prev = start_angle[0] 
    for i in radians[:-1]: 
        start_angle.append(i + prev) 
        prev = i + prev 
    
    # ending angle values 
    end_angle = start_angle[1:] + [math.radians(0)] 
    
    # center of the pie chart 
    x = 0
    y = 0
    
    # radius of the glyphs 
    radius = 1
    
   
    
    # plotting the graph 
    for i in range(len(types)): 
        p.wedge(x, y, radius, 
                    start_angle = start_angle[i], 
                    end_angle = end_angle[i], 
                    color = palette[i],
                    legend_label = types[i]) 
    
    return p
