This project scrape the rent information from http://www.mckinley.com/apartments


To use this program, the following API keys are needed:
1.plotly API
2.mapbox_access_token
3.Google Places API


**secrets file format:
**google_places_key = '*******'
**mapbox_access_token= '*******'
**user_name = '*******'  ##user_name is the username for plotly website
**user_api='*****'       ##user_api is plotly API



For more information, please see here:

Plotly User Guide in Python:   https://plot.ly/python/user-guide

Documentation on the Google Places API: https://developers.google.com/places/web-service/search. 


*Project Structure:

The entire project mainly has four parts:

1. Get data from website and create the cache file. (call function "get_communities_for_state(state)")
2. Create a DB file and json files to store the data. (call function "create_nwe_table()" and "insert_data()" )
3. Query data from the DB file or json files, and plot the result. (for example, call function "address_info(community)" and"plot_location(community)")
4. The interactive part. (call function "interactive()")


Use class "community" to store the community's name, phone, web, street, city, state, zipcode.

Use three dictionaries to store the information:

1. Communities: initial data scraped from website, which contains communities' name, phone, web, street, city, state, zipcode.
2. Rent: information of rent details, including the number of bedroom, the number of bathroom, rent, area.
3. feature: information about communities's features, for example, swimming pool, parking plot, fitness center etc.


*User Guide:

"state" : It will return community list of certain state.
 
	For example, input "state Michigan", it will return all communities'names which are in Michigan.

	As for now, only five states are available. [Florida, Michigan, Georgia, illinois, indiana]

"call" : input "call" + certain community's name. It will return 5 options, to get the relative information,
	just input the number in front of each option.

	For example: input "call Traver Ridge"

	"1. Contact Information"  	 return community's phone number, fax, website

	"2. Address"              	 return community's address, e.g. 2395 Leslie Circle Ann Arbor MI 48105

	"3. Community Features"	  	 return all communty's features

	"4. Details"		  	 return table of rent information, including type, bedroom, bathroom, rent, area

	"5. Download Community Site Map" Download the community's siteplan in your commuter.


	***To finish this part and go back to search another community, input "go back"


"compare": input "compare". It will ask you which two communities would you like to choose, then, input two communities'names, use ',' to seperate. 

	e.g. "Traver Ridge,Evergreen" (NO SPACE between two names)

	this will return a barchart to compare the rent of these two communities.

	y axis is the rent, unit is $, x is the room type in each community. 

	User can compare the rent of same type room of two communities. 


"map":	input "map" + community's name.
	 e.g. "map Traver Ridge". It will return a plotly map of community's location.


"exit": To finish this program.
