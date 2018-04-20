## final project
##Yizhen Qian

import requests
import json
from bs4 import BeautifulSoup
import secrets
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import plotly
import sqlite3
import webbrowser

plotly.tools.set_credentials_file(username=secrets.user_name, api_key=secrets.user_api)


###PART 1 preparation and get the data####

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

###define class:
class community():
    def __init__(self, name=None, phone=None, web=None, zip=None, city=None, state=None, street=None, dict=None):
        if dict is None:
            self.name = name
            self.phone = phone
            self.web = web
            self.street = street
            self.city = city
            self.state = state
            self.zip = address_zip
        else:
            self.name = dict['name']
            self.phone = dict['phone']
            self.web = dict['web']
            self.street = dict['street']
            self.city = dict['city']
            self.state = dict['state']
            self.zip = dict['zip']

    def __str__(self):
        return self.name + self.street+', '+self.city+', '+self.state+' '+self.zip

#define the function of chache file:

def make_request_using_cache(url):
    unique_ident = url

    if unique_ident in CACHE_DICTION:
        #print('get chache data')
        return CACHE_DICTION[unique_ident]

    else:
        #print('get new data')
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

def caching_state(state_abbr):

    base_url = 'http://www.mckinley.com/apartments/'
    details_url = base_url+str(state_abbr)
    page_text = make_request_using_cache(details_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    return page_soup

def caching_community(name):

    details_url = get_community_website(name)
    page_text = make_request_using_cache(details_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    return page_soup

## Get communities of specified state
## it will update dictionary which key is community's name
## and value is community's name and website.
Communities = {}
Rent={}
feature={}
def get_communities_for_state(state_abbr):

    soup=caching_state(state_abbr)
    community_name = soup.find_all(class_='cd-name community-url')
    Community = {}
    class_list=[]
    for object in community_name:
        Community[object.h2.text.replace('\n','')]={'name':object.h2.text.replace('\n',''),'web':object.a['href']}
        Communities[object.h2.text.replace('\n','')]={'name':object.h2.text.replace('\n',''),'web':object.a['href']}

##update community dictionnary of basic information, such as address,contact information, fax .ect.

    for item in Community:
        inner_dict=Community[item]
        details_soup=caching_community(inner_dict['name'])

        name = details_soup.find(id='main-content-name')
        address_street = details_soup.find(class_='street-address')
        address_zip = details_soup.find(class_='postal-code')
        address_city = details_soup.find(class_='locality')
        address_state = details_soup.find(class_='region')
        phone = details_soup.find('div',class_='tel')
        fax = details_soup.find(class_='fax')
        if fax is None:
            Communities[name.h1.text].update( {'name':name.h1.text,'street':address_street.text,'city':address_city.text,'state':address_state.text,'zip':address_zip.text,'phone':phone.text,'fax':None})
        else:
            Communities[name.h1.text].update( {'name':name.h1.text,'street':address_street.text,'city':address_city.text,'state':address_state.text,'zip':address_zip.text,'phone':phone.text,'fax':fax.text})

        class_list.append(community(dict=Communities[name.h1.text]))
## update a dictionary of rent information, including bedroom, bathroom, area, rent

        bed_chunk = details_soup.find_all(class_='floorplan-beds')
        bath_chunk = details_soup.find_all(class_='floorplan-baths')
        rent_chunk = details_soup.select('div.floorplan-rent span')
        aqft_chunk_raw = details_soup.find_all(class_='floorplan-sqft')

        aqft_chunk=[]
        for i in aqft_chunk_raw:
            area=''.join(ele for ele in i.text if ele.isdigit())
            aqft_chunk.append(area)

        rent_dict_each={inner_dict['name']:{}}
        count = 1
        for bed in bed_chunk:
            detail_dict={'type'+str(count):{'bed':bed.text.replace('\n','')}}
            rent_dict_each[inner_dict['name']].update(detail_dict)
            count+=1

        count = 1
        for bath in bath_chunk:
            rent_dict_each[inner_dict['name']]['type'+str(count)].update({'bath':bath.text.replace('\n','')})
            count += 1
        count = 1
        for rent in rent_chunk:
            rent_dict_each[inner_dict['name']]['type'+str(count)].update({'rent':rent.text})
            count += 1
        count = 1
        for area in aqft_chunk[1:]:
            rent_dict_each[inner_dict['name']]['type'+str(count)].update({'area':area})
            count += 1

        Rent.update(rent_dict_each)

        #get the community feature
        feature_chunk = details_soup.select('div.community-section ul li')
        feature_list=[]
        for f in feature_chunk:
            feature_list.append(f.text.replace('\n',''))
        feature[inner_dict['name']]=feature_list

    ##return a list of class community
    return class_list

##return the website of one specified community this function is the preparation for caching each community.
def get_community_website(name):
    base_url = 'http://www.mckinley.com'
    additional_url=Communities[name]['web']
    details_url = base_url+additional_url
    return details_url


##PART 2 Store data in DB file or json file##

#write out file, this function will create json file for certain dictionary
def output_json(dictionary,name):
    result_file_name = name +'.json'
    rf = open(result_file_name, 'w')
    rf.write(json.dumps(dictionary))
    rf.close()


#load_data function
def load_data(name):
    result_file_name = name+'.json'
    result_file = open(result_file_name, 'r')
    contents = result_file.read()
    result_dict = json.loads(contents)
    result_file.close()
    return result_dict

## create db file and table
DBNAME = 'Apartments.db'
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()

def create_new_table():
    statement = '''DROP TABLE IF EXISTS 'Communities'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''CREATE TABLE Communities (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT,
        'StreetAddress' TEXT ,
        'City' TEXT,
        'State' TEXT,
        'Postcode'INTEGER,
        'Phone'TEXT,
        'Fax'TEXT,
        'website'TEXT
        )
    '''

    cur.execute(statement)
    conn.commit()
    statement = '''DROP TABLE IF EXISTS 'Details'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''CREATE TABLE Details (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Community' TEXT ,
        'CommunityId'INTEGER REFERENCES Communities(Id),
        'Bedroom' TEXT ,
        'Bathroom' TEXT ,
        'Rent' TEXT,
        'Area'INTEGER
        )
    '''
    cur.execute(statement)
    conn.commit()

##database insert function

def insert_data():
    for i in Communities:
        insertion = (None,Communities[i]["name"],Communities[i]["street"],Communities[i]["city"],Communities[i]["state"],Communities[i]["zip"],Communities[i]["phone"],Communities[i]["fax"],Communities[i]["web"])
        statement = 'INSERT INTO "Communities" '
        statement += 'VALUES (?,?, ?, ?, ?, ?, ?, ?,?)'
        cur.execute(statement, insertion)
        conn.commit()


    for i in Rent:
        type_dict=Rent[i]
        for j in type_dict:
            insertion = (None,i,None,type_dict[j]["bed"],type_dict[j]["bath"],type_dict[j]["rent"],type_dict[j]["area"])
            statement = 'INSERT INTO "Details" '
            statement += 'VALUES (?,?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
            conn.commit()

    # insert foreign key in rent table:
    statement='''SELECT Id, Name FROM Communities'''
    id_result=cur.execute(statement)
    id_dict={}
    for row in id_result:
        id_dict[row[1]]=row[0]
    for id in id_dict:
        statement = '''UPDATE Details SET CommunityId = '''+str(id_dict[id])+' WHERE Community= "'+str(id) +'"'
        cur.execute(statement)
    conn.commit()


###PART 3 function of query data and plot the map and bar chart##

def select_state(state):
    statement = '''SELECT Name FROM Communities'''
    statement += ' WHERE State = "' +state+'"'
    result_list = cur.execute(statement)
    return result_list

def contact_information(community):
    statement = '''SELECT Phone, Fax, website FROM Communities'''
    statement += ' WHERE Name = "'+community+'"'
    result = cur.execute(statement)
    return result


def address_info(community):
    statement = '''SELECT StreetAddress, City, State, Postcode From communities'''
    statement += ' WHERE Name = "'+community+'"'
    result = cur.execute(statement)
    return result

def feature_info(community):
    with open('feature.json',encoding="utf8") as json_data:
        data = json.load(json_data)
    feature = data[community]
    return feature

def details_info(community):
    statement = '''SELECT Bedroom, Bathroom, Rent, Area FROM Details'''
    statement += ' WHERE Community = "'+community+'"'
    result = cur.execute(statement)
    return result

def community_map(community):
    statement = '''SELECT website From Communities'''
    statement +=' WHERE Name = "' +community +'"'
    result = cur.execute(statement)
    for i in result:
        url_D = i[0]
    details_url = "http://www.mckinley.com"+url_D
    page_text = make_request_using_cache(details_url)
    soup = BeautifulSoup(page_text, 'html.parser')
    map = soup.find(id="siteplan-image")
    map_web = map['href']
    return map_web

def plot_compartion(community1,community2):
    statement = '''SELECT Rent From Details'''
    statement += ' WHERE Community ="'+community1+'"'
    rent_list_1=[]
    x_list_1=[]
    result = cur.execute(statement)
    count=1
    for row in result:
        a=row[0].split()
        rent_list_1.append(a[0])
        x_list_1.append("Type"+str(count))
        count += 1
    statement = '''SELECT Rent From Details'''
    statement += ' WHERE Community ="'+community2+'"'
    rent_list_2=[]
    x_list_2=[]
    result = cur.execute(statement)
    count=1
    for row in result:
        a=row[0].split()
        rent_list_2.append(a[0])
        x_list_2.append("Type"+str(count))
        count += 1
    return rent_list_1,x_list_1,rent_list_2,x_list_2

def plot_bar_chart(rent_1,x_1,rent_2,x_2,community1,community2):
    trace1 = go.Bar(
        x=x_1,
        y=rent_1,
        name=community1
    )
    trace2 = go.Bar(
        x=x_2,
        y=rent_2,
        name=community2
    )

    data = [trace1, trace2]
    layout = go.Layout(
        barmode='group'
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='grouped-bar')

def text_search_for_community(community):
    text_search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' +community +'&radius=10000&key='+secrets.google_places_key
    response = requests.get(text_search_url).json()
    result = response["results"]
    if len(result) == 0:
        return None, None
    else:
        lat=result[0]["geometry"]["location"]["lat"]
        lng=result[0]["geometry"]["location"]["lng"]
        return str(lat), str(lng)

def plot_location(community):
    lat_1,lon_1 = text_search_for_community(community)
    lat_list=[]
    lon_list=[]
    lat_list.append(lat_1)
    lon_list.append(lon_1)
    data = Data([
        Scattermapbox(
            lon = lon_list,
            lat = lat_list,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star'
                ),
            text = community,
        )
    ])


    min_lat = 1000
    max_lat = -1000
    min_lon = 1000
    max_lon = -1000


    if float(lat_1) < min_lat:
        min_lat = float(lat_1)
    if float(lat_1) > max_lat:
        max_lat = float(lat_1)

    if float(lon_1) < min_lon:
        min_lon = float(lon_1)
    if float(lon_1) > max_lon:
        max_lon = float(lon_1)


    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
            tittle = "community location",
            geo = dict(
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                ),
            hovermode='closest',
            mapbox=dict(
                accesstoken=secrets.mapbox_access_token,

        ),
    )


    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='community_location' )

##PART 4 interaction part##
def interactive():
    command=""
    while command != "exit":
        command = input("Hi, What can I do for you?")
        word_list = command.split(' ',1)
        if "state" in word_list:
            word = word_list[1]
            result = select_state(word)
            count=1
            for row in result:
                print(str(count)+' '+row[0])
                count += 1
        elif "call" in word_list:
            community = word_list[1]
            print('1. Contact Information')
            print('2. Address')
            print('3. Community Features')
            print('4. Details')
            print('5. Download Community Map')

            call = input("Which part are you interested in?")

            while call != "go back":
                if call == str(1):
                    result = contact_information(community)
                    for row in result:
                        print('Phone: '+str(row[0]))
                        print('Fax: '+str(row[1]))
                        print('Website: http://www.mckinley.com'+str(row[2]))
                elif call ==str(2):
                    result = address_info(community)
                    for row in result:
                        print(row[0]+' '+row[1]+' '+row[2]+' '+str(row[3]))
                elif call ==str(3):
                    result = feature_info(community)
                    for item in result:
                        print(item)
                elif call == str(4):
                    result = details_info(community)
                    type = 1
                    for row in result:
                        s = [" %-12s ", '   '," %-12s ", '   '," %-12s ", '   '," %-15s ", '   '," %-12s "]
                        print(''.join(s) % ('Type '+str(type),str(row[0]),str(row[1]),str(row[2]),str(row[3])+'sq.ft'))
                        type += 1
                elif call ==str(5):
                    result = community_map(community)
                    webbrowser.open(result)
                elif call == "exit":
                    print('Bye~')
                    break

                else:
                    print("I don't know what's this")

                call = input("Which part are you interested in?")

        elif "compare" in word_list:
            coms = input("please select two communities:")
            community1, community2 = coms.split(',')
            y_1,x_1,y_2,x_2 = plot_compartion(community1,community2)
            plot_bar_chart(y_1,x_1,y_2,x_2,community1,community2)

        elif "map" in word_list:
            community = word_list[1]
            plot_location(community)

        elif command == "exit":
             print("Bye~")

        else:
            print("I don't know what's this")

##implement function to scrape data from website and store them in DB file and json file
### if initialize the entire project is needed, uncomment the following function:

#state_list = ['Florida','Michigan','Georgia','illinois','indiana']
#for i in state_list:
#    get_communities_for_state(i)
#
#output_json(Communities,'Communities')
#output_json(Rent,'Rent')
#output_json(feature,'feature')
#
#create_new_table()
#insert_data()


if __name__=="__main__":
    interactive()
    conn.close()
