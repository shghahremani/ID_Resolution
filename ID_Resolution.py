from __future__ import print_function, unicode_literals
import requests, json
from tabulate import tabulate
from fuzzywuzzy import fuzz
import pandas as pd
from linkedin_api import Linkedin
from facepplib import FacePP, exceptions
import cv2
from PIL import Image
from urllib.request import urlopen
import face_recognition
import numpy as np
import pickle
import webbrowser
from bs4 import BeautifulSoup
from googlesearch import search
####
#name1=james patterson
#name2=Sarah Stockdale
#name3=ana santos
############take input from user
def get_search_user_info():
    full_name = input("Enter full_name: ")
    # middle_name = input("Enter middle_name: ")
    location_country = input("Enter location_country: ")
    job_title = input("Enter job_title: ")

    return full_name, location_country, job_title

################################## replace none values function
def replaceNone(data_dict, v, rv):
  for key in data_dict.keys():
    if data_dict[key] == v:
      data_dict[key] = rv
    elif type(data_dict[key]) is dict:
      replaceNone(data_dict[key], v, rv)

######################### job title generator
def find_job_catagories(df,keyword):

    max = 0
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
############################### fetch data from people data labs API
def people_data_labs(SQL_QUERY,size):
    # Set your API key
    API_KEY = "465695f1f06d1dbe00b51961742fe0b0d331ddbb3935ed919472774158b6fb23"
    # Set the Person Search API URL
    PDL_URL = "https://api.peopledatalabs.com/v5/person/search"
    # Set headers
    HEADERS = {
        'Content-Type': "application/json",
        'X-api-key': API_KEY}

    PARAMS = {
        'sql': SQL_QUERY,
        'size': size,
        'pretty': True}
    response = requests.get(PDL_URL,headers=HEADERS,params=PARAMS).json()
    with open('pdl.json', 'w') as f:
        json.dump(response, f)

    f = open('pdl.json')
    response = json.load(f)
    return response



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

def query_generator(full_name, location_country, job_title):
    df = pd.read_csv('job_title/synonym_job_titles_for_search.csv')
    str_d = ""
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
      categories = find_job_catagories(df, job_title)
      qury = job_titile_quiry_generator(categories, str_d, job_title)
      SQL_QUERY = \
          str('SELECT * FROM person ' \
              'WHERE full_name=') + str('\'') + str(full_name) + str('\'') + \
          str(' AND ') + str('(') + qury + str(')') + \
          str(';')
    else:
      categories = find_job_catagories(df, job_title, max)
      qury = job_titile_quiry_generator(categories, str_d, job_title)
      SQL_QUERY = \
          str('SELECT * FROM person ' \
              'WHERE full_name=') + str('\'') + str(full_name) + str('\'') + \
          str(' AND ') + str('location_country=') + str('\'') + str(location_country) + str('\'') + \
          str(' AND ') + str('(') + qury + str(')') + \
          str(';')
    return SQL_QUERY



# Pass the parameters object to the Person Search API
def check_vali_linkden_url(url):
        instagram_url = f"https://{url}/"
        try:
            r = requests.get(instagram_url)
            print(instagram_url + "\tStatus: " + str(r.status_code))
            valid=True
        except Exception as e:
            print(instagram_url + "\tNA FAILED TO CONNECT\t" + str(e))
            valid=False
        return valid

##############  find linkedin profile url using Proxycurl
def find_linkdin_profile_pic(linkedin_url):
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/person/profile-picture'
    api_key = 'q1e40eHlNSBbJWdKKrHesw'

    header_dic = {'Authorization': 'Bearer ' + api_key}
    params = {
        'linkedin_person_profile_url': linkedin_url,
        'use_cache': 'No'
    }
    print(params)
    #exit()
    response = requests.get(api_endpoint,
                            params=params,
                            headers=header_dic)
    #print(response)
    check_curl_output = '/proxycurl/media/imgs/placeholder-profile.png'
    #print(response.status_code)
    if response.status_code==200:

        data = response.json()
        print(data['tmp_profile_pic_url'])

        return data['tmp_profile_pic_url']
    else:
       return check_curl_output
    # with open('proxcycurl.json', 'w') as f:
    #     json.dump(data, f)
    #
    # f = open('proxcycurl.json')
    # data = json.load(f)


##################### generate all the usernames with same names
def find_instagram_profiles(full_name):
    url = "https://instagram-data1.p.rapidapi.com/user/search"

    querystring = {"keyword": full_name}

    headers = {
        "X-RapidAPI-Key": "443161a19bmshf7fda97869ab8ffp114388jsn56b04432ae70",
        "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    with open('mydata.json', 'w') as f:
        json.dump(response.json(), f)

    f = open('mydata.json')
    response = json.load(f)["users"]
    print(response)
    usernames=[]
    profile_pic_url=[]
    for records in response:
        usernames.append(records['user']['username'])
        profile_pic_url.append(records['user']['profile_pic_url'])

    return usernames, profile_pic_url
# text = response.content
def face_comparing( image1, image2):
    img1 = Image.open(urlopen(image1))
    image1 = np.array(img1)
    rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    ## cnn detection
    boxes1 = face_recognition.face_locations(rgb, model='hog')
    encodings1 = face_recognition.face_encodings(rgb, boxes1)
    # read 2nd image and store encodings
    img2 = Image.open(urlopen(image2))
    image2 = np.array(img2)
    rgb = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
    boxes2 = face_recognition.face_locations(rgb, model='hog')
    #print(boxes)
    encodings2 = face_recognition.face_encodings(rgb, boxes2)
    matches = face_recognition.compare_faces(encodings1, encodings2)
    print(matches)
    index=0
    result = False
    if len(matches)==0:
        return result
    for (x, y, w, h) in boxes1:
        cv2.rectangle(image1, (h, w), (y, x), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        if matches[index]==True:
            cv2.putText(image1, "True", (h + 6, w - 6), font, 1.0, (255, 255, 255), 1)
            result=True
        else:
            cv2.putText(image1, "False", (h + 6, w - 6), font, 1.0, (255, 255, 255), 1)
        index = index + 1
    resized1 = cv2.resize(image1, (256, 256), interpolation=cv2.INTER_AREA)
    resized2 = cv2.resize(image2, (256, 256), interpolation=cv2.INTER_AREA)

    horizontal_concat = np.concatenate((resized1, resized2), axis=1)
    cv2.imshow("Horizontal plot", horizontal_concat)
    # cv2.imshow("Faces found", image)
    cv2.waitKey(0)

    return result
############################ We don't use this function/ compare two images to see if they are similar
def face_comparing_using_api( Image1, Image2):
    api_key = 'xQLsTmMyqp1L2MIt7M3l0h-cQiy0Dwhl'
    api_secret = 'TyBSGw8NBEP9Tbhv_JbQM18mIlorY6-D'

    try:
        print("\t\t\t" + "Photo Comparing App\n")
        #         # call api
        app = FacePP(api_key=api_key,
                      api_secret=api_secret)
        # funcs = [
        #     face_detection,
        #     # face_comparing_localphoto,
        #     # face_comparing_websitephoto,
        #     faceset_initialize,
        #     face_search,
        #     face_landmarks,
        #     dense_facial_landmarks,
        #     face_attributes,
        #     beauty_score_and_emotion_recognition
        #
    except exceptions.BaseFacePPError as e:
        print('Error:', e)
    print('Comparing Photographs......')
    print('-' * 30)



    # Comparing Photos

    try:
        cmp_ = app.compare.get(image_url1=Image1,
                               image_url2=Image2)
        print('Photo1', '=', cmp_.image1)
        print('Photo2', '=', cmp_.image2)
        if cmp_.confidence > 70:
            print(cmp_.confidence)
            print('Both photographs are of same person......')
            return True
        else:
            print(cmp_.confidence)
            print('Both photographs are of two different persons......')
            return False
    except Exception as e:
        print(str(e))
        return False



############### find instagram accounts_url
def find_instagram_profile_url(name,linkedin_profile_photo_url,usernames, photo_urls):
    #usernames, photo_urls=find_instagram_profiles(name)
    instagram_url = "Not found"
    i=0
    for url in photo_urls:

        username=usernames[i]
        i+=1
        if face_comparing(url,linkedin_profile_photo_url):

            instagram_url = f"https://www.instagram.com/{username}/?_a=1"
            break

        else:
            continue
    return instagram_url

# Check for successful response

def generate_output(response,usernames, photo_urls):
    col_names = ["full_name", "first_name", "middle_name", "last_name", "gender", "location_country", "job_title",
                 "industry", "job_company_name", "countries", "linkedin_url", "linkedin_username", "instagram_url",
                 "facebook_url", "facebook_username", "twitter_url",
                 "twitter_username", "work_email", "personal_emails", "mobile_phone"]
    data_table = []
    if response["status"] == 200:
        data = response['data']
        with open("my_pdl_search.jsonl", "w") as out:
            for record in data:
                # print(record["linkedin_url"])
                # exit()
                check_curl_output='/proxycurl/media/imgs/placeholder-profile.png'
                linkedin_profile_photo_url = find_linkdin_profile_pic(record["linkedin_url"])
                print(linkedin_profile_photo_url)
                if check_curl_output!=linkedin_profile_photo_url:
                    print('yes')
                    linkedin_url=record["linkedin_url"]
                    linkedin_url= f"https://{linkedin_url}/"
                    instagram_url=find_instagram_profile_url(record["full_name"],linkedin_profile_photo_url,usernames, photo_urls)
                    data_table.append( [record["full_name"], record["first_name"], record["middle_name"], record["last_name"], record["gender"],record["location_country"],record["job_title"],record["industry"],  record["job_company_name"], record["countries"]
                               , linkedin_url, record["linkedin_username"], instagram_url,record["facebook_url"], record["facebook_username"],
                               record["twitter_url"],record["twitter_username"], record["work_email"], record["personal_emails"], record["mobile_phone"]])

                    out.write(json.dumps(record) + "\n")
        print(f"successfully grabbed {len(data)} records from pdl")

        print(f"{response['total']} total pdl records exist matching this query")
        output = tabulate(data_table, headers=col_names, tablefmt="fancy_grid", showindex="always")
        print(output)
    else:
        print("NOTE. The carrier pigeons lost motivation in flight. See error and try again.")
        print("error:", response)
        data_table.append(
              ["-", "-", "-", "-", "-",
               "-", "-", "-", "-",
               "-"
                  , "-", "-", "-", "-",
               "-","-",
               "-", "-", "-", "-"
               ])



        #### save output
        # with open("Data\/ryon_travis_name", "wb") as fp:
        #     pickle.dump(data_table, fp)
        #
        # with open("API_out", "rb") as fp:
        #   data_table=pickle.load(fp)
        print(data_table)

        #data=[[record["full_name"]], [record["first_name"]],[record["middle_name"]],[record["last_name"]],[record["gender"]],[record["linkedin_url"]],[record["linkedin_username"]],[record["facebook_url"]],[record["facebook_username"]],[record["twitter_url"]],
        #   [record["twitter_username"]],[record["work_email"]],[record["personal_emails"]],[record["mobile_phone"]],[record["industry"]],[record["job_title"]],[record["job_company_name"]],[record["location_country"]],[record["interests"]],[record["skills"]],[record["countries"]]]

        output=tabulate(data_table, headers=col_names, tablefmt="fancy_grid", showindex="always")
        print(output)



def main():

    full_name, location_country, job_title=get_search_user_info()
    SQL_QUERY=query_generator(full_name, location_country, job_title)
    response=people_data_labs(SQL_QUERY,6)
    usernames, photo_urls = find_instagram_profiles(full_name)
    #linkdin_profile_pic=find_linkdin_profile_pic()
    generate_output(response,usernames, photo_urls)



if __name__ == "__main__":
    main()
