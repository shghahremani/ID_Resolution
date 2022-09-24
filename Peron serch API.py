import requests, json
from tabulate import tabulate

# Set your API key
API_KEY = "e52a8fecc62240a46babb046d32c8c4c2778f11904fd2b479a136e0b3d964ddf"

# Set the Person Search API URL
PDL_URL = "https://api.peopledatalabs.com/v5/person/search"

# Set headers
HEADERS = {
  'Content-Type': "application/json",
  'X-api-key': API_KEY
}

# function inorder to replace null values with _
def replaceNone(data_dict, v, rv):
  for key in data_dict.keys():
    if data_dict[key] == v:
      data_dict[key] = rv
    elif type(data_dict[key]) is dict:
      replaceNone(data_dict[key], v, rv)

############take input from user
full_name = input("Enter full_name: ")
# middle_name = input("Enter middle_name: ")
location_country = input("Enter location_country: ")
job_title = input("Enter job_title: ")
# skills = input("Enter skills: ")
# linkedin_username = input("Enter linkedin_username: ")
# facebook_username = input("Enter facebook_username: ")
# twitter_username = input("Enter twitter_username: ")


# Create an SQL query
SQL_QUERY = \
str('SELECT * FROM person '\
    'WHERE full_name=')+ str('\'')+str(full_name)+ str('\'')+\
str(' AND ') +str('(')+str('location_country=')+ str('\'')+str(location_country)+ str('\'')+ \
str(' OR job_title=')+ str('\'')+str(job_title)+ str('\'')+str(')')+\
str(';')
# print(SQL_QUERY)
# exit()
# Create a parameters JSON object
PARAMS = {
  'sql': SQL_QUERY,
  'size': 3,
  'pretty': True
}

# Pass the parameters object to the Person Search API
response = requests.get(
  PDL_URL,
  headers=HEADERS,
  params=PARAMS
).json()

data_table=[]
# Check for successful response
if response["status"] == 200:
  data = response['data']
  # Write out each profile found to file
  with open("my_pdl_search.jsonl", "w") as out:
    for record in data:
      replaceNone(record, None, "_")
      data_table.append( [record["full_name"], record["first_name"], record["middle_name"], record["last_name"], record["gender"],record["location_country"],record["job_title"],record["industry"],  record["job_company_name"],record["interests"],record["skills"], record["countries"]
               , record["linkedin_url"], record["linkedin_username"], record["facebook_url"], record["facebook_username"],
               record["twitter_url"],
               record["twitter_username"], record["work_email"], record["personal_emails"], record["mobile_phone"]
               ])

      out.write(json.dumps(record) + "\n")
  print(f"successfully grabbed {len(data)} records from pdl")
  print(f"{response['total']} total pdl records exist matching this query")

else:
  print("NOTE. The carrier pigeons lost motivation in flight. See error and try again.")
  print("error:", response)

#### craete table



col_names=["full_name", "first_name","middle_name","last_name","gender","location_country","job_title","industry","job_company_name","interests","skills","countries","linkedin_url","linkedin_username","facebook_url","facebook_username","twitter_url",
  "twitter_username","work_email","personal_emails","mobile_phone"]
# data=[[record["full_name"]], [record["first_name"]],[record["middle_name"]],[record["last_name"]],[record["gender"]],[record["linkedin_url"]],[record["linkedin_username"]],[record["facebook_url"]],[record["facebook_username"]],[record["twitter_url"]],
#   [record["twitter_username"]],[record["work_email"]],[record["personal_emails"]],[record["mobile_phone"]],[record["industry"]],[record["job_title"]],[record["job_company_name"]],[record["location_country"]],[record["interests"]],[record["skills"]],[record["countries"]]]

#print(data)
print(tabulate(data_table, headers=col_names, tablefmt="fancy_grid", showindex="always"))


