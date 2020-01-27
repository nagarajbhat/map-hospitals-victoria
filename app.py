
#dependencies
import pandas as pd
import folium
from folium.plugins import HeatMap

#data
data = pd.read_csv('./data/hospital_locations.csv')
df = data.filter(["Y","X","LabelName","Type","StreetNum","RoadName","RoadType","Postcode"])
df_postcode = data.groupby(['Postcode'],as_index=False)
postcode_count = df_postcode.count().filter(["Postcode","FID"])
postcode_count = postcode_count.sort_values(by="FID",ascending=False)

#locality data
australian_postcodes = pd.read_csv('./data/australian_postcodes.csv')
vic_postcodes = australian_postcodes[australian_postcodes["state"]=='VIC']
vic_postcodes = vic_postcodes.filter(["postcode","locality","lat",'long'])
vic_postcodes.head(5)

#merge both data
df_merged  = postcode_count.merge(vic_postcodes,left_on='Postcode',right_on='postcode',how="inner")
df_merged = df_merged.dropna()
top_localities = df_merged.sort_values(by="FID",ascending=False)
top_localities

m = folium.Map(location=[-38.0,145], control_scale=True, zoom_start=10,attr = "text some",tiles=None)
df_copy = df.copy()
df_copy['count'] = 1

feature_group0 = folium.FeatureGroup(name='Hospitals',overlay=False).add_to(m)
feature_group1= folium.FeatureGroup(name='Locality',overlay=False).add_to(m)
feature_group2 = folium.FeatureGroup(name='HeatMap of hospitals',overlay=False).add_to(m)

for i in range(0,len(df_copy)):
    html="""
    <h4> Hospital name: </h4>""" + str(df_copy.iloc[i]['LabelName'])+ \
    """<h4>Type:</h4>""" + str(df_copy.iloc[i]['Type']) +" Hospital" +\
    """<h4>Address:</h4>""" + str(df_copy.iloc[i]['StreetNum'])+" "+ str(df_copy.iloc[i]['RoadName'])+" "+ str(df_copy.iloc[i]['RoadType'])
    
    #IFrame 
    iframe = folium.IFrame(html=html, width=200, height=300)
    popup = folium.Popup(iframe, max_width=2650)
    
    folium.Marker(
    location=[df_copy.iloc[i]['Y'], df_copy.iloc[i]['X']],
    radius=float(3),
    popup=popup,
    tooltip=str(df_copy.iloc[i]['LabelName']),
    icon=folium.Icon(color='green',icon='medkit',prefix="fa"),
    legend_name ="hospitals"
    ).add_to(feature_group0)

    

    
df_merg = df_merged.copy()
df_merg['count'] = 1

# create Folium circle
for i in range(0,len(df_merg)):
    # html to be displayed in the popup 
    html="""
    <h4> Locality Name: </h4>""" + str(df_merg.iloc[i]['locality'])+\
    """<h4>Postcode:</h4>""" + str(df_merg.iloc[i]['postcode'])+\
    """<h4>Number of hospitals:</h4>""" + str(df_merg.iloc[i]['FID'])
    
    #IFrame 
    iframe = folium.IFrame(html=html, width=200, height=300)
    popup = folium.Popup(iframe, max_width=2650)
    
    folium.Circle(
    location=[df_merg.iloc[i]['lat'], df_merg.iloc[i]['long']],
    radius=float(df_merg.iloc[i]['FID']*200),
    popup=popup,
    tooltip=str(df_merg.iloc[i]['locality']),
    color='crimson',
     fill=True,
     fill_color='green'
    ).add_to(feature_group1)

HeatMap(data=df_copy[['Y', 'X', 'count']].groupby(['Y', 'X']).sum().reset_index().values.tolist(),gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'},radius=15, max_zoom=13).add_to(feature_group2)

folium.TileLayer('OpenStreetMap',overlay=True,name="color mode").add_to(m)     
folium.TileLayer('cartodbdark_matter',overlay=True,name="dark mode").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

m.save("./files/app.html")


m
