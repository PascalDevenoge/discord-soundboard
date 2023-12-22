import json
import logging
from queue import Empty
import secrets
from typing import Any
import uuid

import data_access
from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask_sqlalchemy import SQLAlchemy
import pydub
from pydub.effects import normalize
from pydub.silence import detect_leading_silence
import server_event

log = logging.getLogger('Web API')


def create_app():
    app = Flask('Soundboard Web API')
    app.secret_key = secrets.token_bytes(16)

    app.logger.addHandler(log)

    db = SQLAlchemy(model_class=data_access._Base)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()

    event_manager = server_event.get_event_manager()

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

    @app.route('/play/<uuid:id>/<float(signed=True, max=30.0):volume>')
    def play_clip(id: uuid.UUID, volume: float):
        if not data_access.track_exists(db.session, id):
            return Response(f'Track {id} does not exist', 404)

        event_manager.signal(server_event.PlayClipEvent(id, volume))
        return Response('', 204)

    @app.route('/play/all')
    def play_all_clips():
        event_manager.signal(server_event.PlayAllClipsEvent())
        return Response('', 204)

    @app.route('/stop')
    def stop_playback():
        event_manager.signal(server_event.StopAllEvent())
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
        resampled = raw_samples.set_channels(
            2).set_sample_width(2).set_frame_rate(48000)

        def trim_leading(
            x: pydub.AudioSegment) -> pydub.AudioSegment: return x[detect_leading_silence(x):]

        def trim_end(x: pydub.AudioSegment) -> pydub.AudioSegment:
            return trim_leading(x.reverse()).reverse()

        trimmed = trim_leading(trim_end(resampled))
        normalized: pydub.AudioSegment = normalize(trimmed, 15.0)

        data_access.save_track(
            db.session, data_access.Track(id, name, normalized, normalized.duration_seconds))

        event_manager.signal(server_event.ClipUploadedEvent(id, name))
        return redirect('/')

    @app.route('/delete/<uuid:id>', methods=['POST'])
    def delete_clip(id: uuid.UUID):
        track_deleted = data_access.delete_track(db.session, id)
        if not track_deleted:
            return Response(f'Track {str(id)} does not exist', 404)
        event_manager.signal(server_event.ClipDeletedEvent(id))
        return Response(f'Track {str(id)} deleted', 204)

    @app.route('/rename/<uuid:id>/<string:new_name>', methods=['POST'])
    def rename_clip(id: uuid.UUID, new_name: str):
        clip_renamed = data_access.update_track_name(db.session, id, new_name)
        if not clip_renamed:
            return Response(f'Track {str(id)} does not exist', 404)
        event_manager.signal(server_event.ClipRenamedEvent(id, new_name))
        return Response(f'Track {str(id)} renamed to {new_name}', 204)

    def format_event(event_name: str, payload: dict[str, Any]):
        return f'event: {event_name}\ndata: {json.dumps(payload)}\n\n'

    @app.route('/listen')
    def event_listen():
        def event_generator():
            try:
                subscription = event_manager.subscribe()
                while True:
                    try:
                        event: server_event.Event = subscription.listen(
                            timeout=5)
                        match event.type:
                            case server_event.EventType.CLIP_UPLOADED:
                                yield format_event('clip-uploaded', {"id": str(event.id), "name": event.name})
                            case server_event.EventType.CLIP_DELETED:
                                yield format_event('clip-deleted', {"id": str(event.id)})
                            case server_event.EventType.CLIP_RENAMED:
                                yield format_event('clip-renamed', {"id": str(event.id), "new_name": event.new_name})
                    except Empty:
                        yield ":keep-alive\n\n"
                    except EOFError:
                        break
            finally:
                log.info("Connection closed")
                subscription.unsubscribe()
        return Response(event_generator(), mimetype='text/event-stream')

    return app
