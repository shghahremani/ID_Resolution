import requests, json
from tabulate import tabulate
from fuzzywuzzy import fuzz
import pandas as pd
import pickle
import webbrowser

# Set your API key
API_KEY = "f6c086477fd542ff51af13f8e5c7f8194b739931e1ab70ca017b3c482accbe49"

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

######################### job title generator

df = pd.read_csv('job_title\synonym_job_titles_for_search.csv')
max=0
def find_job_catagories(df,keyword,max):
    for i in range(0,len(df)):
        for j in range(0,16):
            # print(str(df.values[136,0]))
            # print(fuzz.ratio(keyword,str(df.values[136,4])))
            # exit()
            if (fuzz.ratio(keyword,str(df.values[i,j]))) > max:
                max=fuzz.ratio(keyword,str(df.values[i,j]))
                index=i
                # print(max)
    nonull_df=df.loc[index,:].copy()
    nonull_df=nonull_df.dropna(inplace=False)

    return nonull_df

str_d=""

# print("Job title categories:", categories)
def job_titile_quiry_generator(categories,sig,job_title):
  for i in range(0,len(categories)):
    # print(non_df[i])
    if i==len(categories)-1:
      sig += str('job_title=')+ str('\'')+str(categories[i])+str('\'')+ str(" OR ")+str('job_title=')+str('\'')+str(job_title)+str('\'')
      # sig += str('job_title=') + str('\'') + str(categories[i]) + str('\'') + str(" OR ") + str('job_title=') + str(
      #     '\'') + str(job_title) + str('\'')

    else:
        sig += str('job_title=')  + str('\'')+str(categories[i]) +str('\'')+ str(" OR ")

  return sig
# print(qury)
# exit()

# skills = input("Enter skills: ")
# linkedin_username = input("Enter linkedin_username: ")
# facebook_username = input("Enter facebook_username: ")
# twitter_username = input("Enter twitter_username: ")

if len(job_title)==0 and len(location_country)==0:

# Create an SQL query
  SQL_QUERY = \
  str('SELECT * FROM person '\
      'WHERE full_name=')+ str('\'')+str(full_name)+ str('\'')+\
  str(';')
  # str(' OR job_title=')+ str('\'')+str(job_title)+ str('\'')+str(')')+\
elif len(job_title)==0 and len(location_country)!= 0:

# Create an SQL query
  SQL_QUERY = \
  str('SELECT * FROM person '\
      'WHERE full_name=')+ str('\'')+str(full_name)+ str('\'')+\
  str(' AND ') + str('location_country=') + str('\'') + str(location_country) + str('\'') + \
  str(';')

elif len(location_country)==0 and len(job_title)!= 0:
  categories = find_job_catagories(df, job_title, max)
  qury = job_titile_quiry_generator(categories, str_d, job_title)
  print("Job title categories:", categories.values)

  SQL_QUERY = \
      str('SELECT * FROM person ' \
          'WHERE full_name=') + str('\'') + str(full_name) + str('\'') + \
      str(' AND ') + str('(') + qury + str(')') + \
      str(';')
else:
  categories = find_job_catagories(df, job_title, max)
  qury = job_titile_quiry_generator(categories, str_d, job_title)
  print("Job title categories:", categories.values)

  SQL_QUERY = \
      str('SELECT * FROM person ' \
          'WHERE full_name=') + str('\'') + str(full_name) + str('\'') + \
      str(' AND ') + str('location_country=') + str('\'') + str(location_country) + str('\'') + \
      str(' AND ') + str('(') + qury + str(')') + \
      str(';')

# print(SQL_QUERY)
# exit()
# Create a parameters JSON object
PARAMS = {
  'sql': SQL_QUERY,
  'size': 5,
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

#### save output
# with open("API_out", "wb") as fp:
#     pickle.dump(data_table, fp)
#

col_names=["full_name", "first_name","middle_name","last_name","gender","location_country","job_title","industry","job_company_name","interests","skills","countries","linkedin_url","linkedin_username","facebook_url","facebook_username","twitter_url",
  "twitter_username","work_email","personal_emails","mobile_phone"]
# data=[[record["full_name"]], [record["first_name"]],[record["middle_name"]],[record["last_name"]],[record["gender"]],[record["linkedin_url"]],[record["linkedin_username"]],[record["facebook_url"]],[record["facebook_username"]],[record["twitter_url"]],
#   [record["twitter_username"]],[record["work_email"]],[record["personal_emails"]],[record["mobile_phone"]],[record["industry"]],[record["job_title"]],[record["job_company_name"]],[record["location_country"]],[record["interests"]],[record["skills"]],[record["countries"]]]

#print(data)
output=tabulate(data_table, headers=col_names, tablefmt="fancy_grid", showindex="always")
print(output)
