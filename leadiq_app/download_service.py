from datetime import datetime
from pytz import utc
from imgur_upload import image_upload
import os
import requests


def image_download(url_list, url_list_success):
    url_list['status'] = 'in-progress'
    url_ary, image_info = [], dict()
    url_ary.extend(url_list['uploaded']['pending'])
    for urls in url_ary:
        if urls.find('/'):
            img_name = urls.rsplit('/', 1)[1]
            hdr = requests.head(urls, allow_redirects=True)
            content_type = hdr.headers.get('content-type')
            if 'text' in content_type.lower() or 'html' in content_type.lower():
                url_list['uploaded']['pending'].remove(urls)
                url_list['uploaded']['failed'].update({urls: "URL File Download Error"})
            else:
                img_obj = requests.get(urls, allow_redirects=True)
                abs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', img_name)
                open(abs_file, 'wb').write(img_obj.content)
                if os.path.isfile(abs_file):
                    image_info.update({urls: abs_file})
                else:
                    url_list['uploaded']['pending'].remove(urls)
                    url_list['uploaded']['failed'].update({urls: "File Does Not Exists"})
    url_ary = None
    image_upload(url_list, url_list_success, image_info)
    if not url_list['uploaded']['pending']:
        url_list['status'] = 'complete'
    else:
        url_list['status'] = 'in-complete'
    url_list['finished'] = utc.localize(datetime.utcnow().replace(microsecond=0)).isoformat()
