from flask import Flask, render_template, Response, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import data_access

import secrets
import logging

from multiprocessing.connection import Client

import event

import pydub
from pydub.silence import detect_leading_silence
from pydub.effects import normalize

import uuid

log = logging.getLogger('Web API')
event_connection = Client('discord-soundboard/event-broker')


def create_app():

    app = Flask('Soundboard Web API')
    app.secret_key = secrets.token_bytes(16)

    app.logger.addHandler(log)

    db = SQLAlchemy(model_class=data_access._Base)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.context_processor
    def utilities():
        def print_debug_message(message):
            log.info(str(message))
            return ''

        return dict(debug=print_debug_message)

    @app.route('/')
    def root_page():
        return render_template('index.html')

    @app.route('/tracks')
    def get_tracks():
        track_infos = data_access.get_all_track_info(db.session)
        return {str(track_info.id): track_info.name for track_info in track_infos}

    @app.route('/play/<uuid:id>/<float:volume>')
    def play_clip(id: uuid.UUID, volume: float):
        if not data_access.track_exists(db.session, id):
            return Response(f'Track {id} does not exist', 404)

        event_connection.send(event.PlayClipEvent(id, 1.0))
        return Response('', 204)

    @app.route('/play/all')
    def play_all_clips():
        event_connection.send(event.PlayAllClipsEvent())
        return Response('', 204)

    @app.route('/stop')
    def stop_playback():
        event_connection.send(event.StopAllEvent())
        return Response('', 204)

    @app.route('/upload', methods=['POST'])
    def upload_clip():
        if 'file' not in request.files or request.files['file'].filename == '':
            log.warn(f'Error during file upload')
            flash('Missing or broken file was uploaded', 'error')
            return redirect('/')
        
        id = uuid.uuid4()
        file = request.files['file']
        name = str.join('.', str.split(file.filename, '.')[:-1])

        raw_samples: pydub.AudioSegment = pydub.AudioSegment.from_file(file)
        resampled = raw_samples.set_channels(2).set_sample_width(2).set_frame_rate(48000)

        trim_leading = lambda x: x[detect_leading_silence(x) : ]
        trim_end = lambda x: trim_leading(x.reverse()).reverse()

        trimmed = trim_leading(trim_end(resampled))
        normalized = normalize(trimmed, 15.0)

        data_access.save_track(db.session, data_access.Track(id, name, normalized))
        return redirect('/')

    return app
