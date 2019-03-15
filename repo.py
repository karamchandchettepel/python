import subprocess
import requests
from datetime import *
import datetime
import dateutil.relativedelta
import sys
from urllib2 import urlopen, Request, HTTPError
from urllib2 import build_opener, HTTPHandler

docker_hub_username = 'dockerhub_username'
docker_hub_password = 'dockerhub_password'

def run_command(command):
    result = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    result = result.stdout.read()
    result_list = result.split('\n')[:-1]
    return result_list
    
def del_tag(namespace, repo, tag, token_list):
    url = 'https://hub.docker.com/v2/repositories/%s/%s/tags/%s/' % (namespace, repo, tag)
    headers = {
        'Authorization': 'JWT %s' % token_list
    }
    request = Request(url=url, headers=headers)
    request.get_method = lambda: 'DELETE'
    try:
        opener = build_opener(HTTPHandler)
        opener.open(request)
        print('%s/%s:%s deleted successfully.' % (namespace, repo, tag))
    except HTTPError as err:
        print("Failed to delete tag %s, exiting." % err)
        sys.exit(1)
    
get_token_cmd = 'curl -s -H "Content-Type: application/json" -X POST -d \'{"username": '+'"'+docker_hub_username+'"'+', "password": '+'"'+docker_hub_password+'"'+'}\' https://hub.docker.com/v2/users/login/ | jq -r .token'
get_token_list = run_command(get_token_cmd)

for token_list in get_token_list:
    get_repo_list_cmd = 'curl -s -H "Authorization: JWT '+token_list+'" https://hub.docker.com/v2/repositories/'+docker_hub_username+'/?page_size=10000 | jq -r '"'.results|.[]|.name'"''
    get_repo_list_final = run_command(get_repo_list_cmd)
    
for i in get_repo_list_final:
    image_tags = 'curl -s -H "Authorization: JWT '+token_list+'" https://hub.docker.com/v2/repositories/'+docker_hub_username+'/'+i+'/tags/?page_size=10000 | jq -r '"'.results|.[]|.name'"''
    image_creation_date = 'curl -s -H "Authorization: JWT '+token_list+'" https://hub.docker.com/v2/repositories/'+docker_hub_username+'/'+i+'/tags/?page_size=10000 | jq -r '"'.results|.[]|.last_updated'"''
    image_tags_list = run_command(image_tags)
    image_creation_date_list = run_command(image_creation_date)
    ####print image_tags_list
    ###print image_creation_date_list
    date_list = []
    for j in image_creation_date_list:
        image_y, image_m, image_d = j.split('T')[0].split('-')
        image_creation_date = date(int(image_y), int(image_m), int(image_d))
        date_list.append(str(image_creation_date))
    date_version_list = zip(date_list, image_tags_list)
    for dv in date_version_list:
        key = dv[0]
        value = dv[1]
        image_y, image_m, image_d = key.split('-')
        image_date = date(int(image_y), int(image_m), int(image_d))
        current_time = datetime.datetime.now()
        date_fnl = current_time + dateutil.relativedelta.relativedelta(days=-1) # days can be replaced by months
        final_y, final_m, final_d = str(date_fnl).split(' ')[0].split('-')
        final_date = date(int(final_y), int(final_m), int(final_d))
       ###### print 'final_time: '+str(final_date)
       ##### print 'image_creation_time: '+str(image_date)
        if image_date >= final_date:
            print 'older -> date:' + str(image_date) + ', repo:'+docker_hub_username+'/'+ i + ', tag:' +value
            del_tag(docker_hub_username, i, value, token_list)

