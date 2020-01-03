from flask import Flask, json, make_response, request, abort, current_app, jsonify, send_from_directory
from datetime import datetime
from collections import OrderedDict
from threading import Thread
from download_service import image_download
from pytz import utc
import random
import os

app = Flask(__name__)

url_list_success = dict(uploaded=[])
job_status = []


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static')
                               , 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Invalid request'}), 500)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/v1/images', methods=['GET'])
def get_image_list():
    return current_app.response_class(json.dumps(url_list_success, indent=2), mimetype="application/json")


@app.route('/v1/images/upload/<job_id>', methods=['GET'])
def get_job_status(job_id):
    job_state = [job_state for job_state in job_status if job_state['id'] == job_id]
    if len(job_state) == 0:
        abort(404)
    return current_app.response_class(json.dumps(job_state[0], indent=2), mimetype="application/json")


@app.route('/v1/images/upload', methods=['POST'])
def upload_images():
    if not request.json or not 'urls' in request.json:
        abort(400)
    input_url = list(set(request.json['urls']))
    job_id = str(random.getrandbits(10))
    current_job = OrderedDict(
        [
            ('id', job_id),
            ('created', utc.localize(datetime.utcnow().replace(microsecond=0)).isoformat()),
            ('finished', None),
            ('status', 'pending'),
            (
                'uploaded',
                OrderedDict([
                    ('pending', input_url),
                    ('complete', []),
                    ('failed', {})
                ])
            )
        ]
    )
    job_status.append(current_job)
    Thread(target=image_download, args=[current_job, url_list_success]).start()
    return current_app.response_class(json.dumps({"jobId": job_id}, indent=2), mimetype="application/json"), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
