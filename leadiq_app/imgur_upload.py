import ConfigParser
from imgurpython import ImgurClient
import requests
import json
import os
from imgurpython.helpers.error import ImgurClientError


def image_upload(url_list, url_list_success, image_info):
    access_token_url = 'https://api.imgur.com/oauth2/token'
    config = ConfigParser.ConfigParser()
    config.read('auth.ini')
    client_id = config.get('credentials', 'client_id')
    client_secret = config.get('credentials', 'client_secret')
    refresh_token = config.get('credentials', 'refresh_token')
    access_data = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    response = requests.request('POST', access_token_url, headers={}, data=access_data, files={}, allow_redirects=False)
    access_token = json.loads(response.text)['access_token']
    if access_token != "":
        try:
            access_object = ImgurClient(client_id, client_secret, access_token, refresh_token)
            for url, local_path in image_info.items():
                upload_config = {
                    'name': url.rsplit('/', 1)[1],
                    'title': url.rsplit('/', 1)[1],
                    'description': 'LeadIQ Test API Upload Service'
                }
                upload_response = access_object.upload_from_path(local_path, config=upload_config, anon=False)
                if upload_response['link'] != '':
                    os.remove(local_path)
                    url_list['uploaded']['pending'].remove(url)
                    url_list['uploaded']['complete'].append(upload_response['link'])
                    if upload_response['link'] not in url_list_success['uploaded']:
                        url_list_success['uploaded'].append(upload_response['link'])
                else:
                    url_list['uploaded']['pending'].remove(url)
                    url_list['uploaded']['failed'].update({url: "Imgur File Upload Error"})
        except ImgurClientError as e:
            print (e.status_code + " " + e.error_message)
