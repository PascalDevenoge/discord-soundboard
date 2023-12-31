import json
import logging
from queue import Empty
import secrets
from typing import Any
import uuid

import data_access
from flask import Flask
from flask import request
from flask import Response
from flask_sqlalchemy import SQLAlchemy
import pydub
from pydub.effects import normalize
from pydub.silence import detect_leading_silence
import server_event

log = logging.getLogger('Web API')


def create_app():
    app = Flask('Soundboard Web API',
                static_folder="../frontend/dist", static_url_path="")
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
        return app.send_static_file('index.html')

    @app.route('/tracks')
    def get_tracks():
        track_infos = data_access.get_all_track_info(db.session)
        return [{'id': track_info.id, 'name': track_info.name, 'length': track_info.length} for track_info in track_infos]

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
            return Response(400, 'Error during file upload')

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
        return Response('', 204)

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
                            case server_event.EventType.PLAY_CLIP:
                                yield format_event('clip-played', {"id": str(event.id)})
                            case server_event.EventType.PLAY_ALL:
                                yield format_event('all-clips-played', {})
                            case server_event.EventType.STOP_ALL:
                                yield format_event('all-clips-stopped', {})
                            case server_event.EventType.CLIP_UPLOADED:
                                yield format_event('clip-uploaded', {"id": str(event.id), "name": event.name})
                            case server_event.EventType.CLIP_DELETED:
                                yield format_event('clip-deleted', {"id": str(event.id)})
                            case server_event.EventType.CLIP_RENAMED:
                                yield format_event('clip-renamed', {"id": str(event.id), "new_name": event.new_name})
                            case server_event.EventType.PLAY_SEQUENCE:
                                yield format_event('sequence-played', {'id': event.id})
                            case server_event.EventType.SEQUENCE_CREATED:
                                yield format_event('sequence-created', {'id': event.id, 'name': event.name})
                            case server_event.EventType.SEQUENCE_DELETED:
                                yield format_event('sequence-deleted', {'id': event.id})
                    except Empty:
                        yield ":keep-alive\n\n"
                    except EOFError:
                        break
            finally:
                log.info("Connection closed")
                subscription.unsubscribe()
        return Response(event_generator(), mimetype='text/event-stream')

    @app.route('/sequences')
    def get_all_sequences():
        sequences = data_access.get_all_sequences(db.session)

        sequence_infos = []
        for sequence in sequences:
            sequence_infos.append(
                {
                    'id': sequence.id,
                    'name': sequence.name,
                    'tracks': [
                        {
                            'uuid': step.clip_id,
                            'volume': step.volume,
                            'delay': step.delay,
                        } for step in sequence.steps
                    ]
                }
            )

        return sequence_infos

    @app.route('/sequences/create', methods=['POST'])
    def create_sequence():
        sequence_data = request.json
        sequence = data_access.Sequence(
            id=-1, name=sequence_data['name'], steps=[])

        for num, step in enumerate(sequence_data['tracks']):
            sequence.steps.append(data_access.SequenceStep(
                id=-1,
                num=num,
                clip_id=uuid.UUID(step['uuid']),
                volume=step['volume'],
                delay=step['delay']
            ))

        id = data_access.save_sequence(db.session, sequence)
        event_manager.signal(
            server_event.SequenceCreatedEvent(id, sequence.name))
        return Response(str(id), 201)

    @app.route('/sequences/delete/<int:id>', methods=['POST'])
    def delete_sequence(id: int):
        deleted = data_access.delete_sequence(db.session, id)
        if not deleted:
            return Response(f'Sequence {id} does not exist', 404)
        else:
            event_manager.signal(server_event.SequenceDeletedEvent(id))
            return Response(f'Sequence {id} deleted', 204)

    @app.route('/sequences/play/<int:id>')
    def play_sequence(id: int):
        if not data_access.sequence_exists(db.session, id):
            return Response(f'Sequence {id} does not exist', 404)

        event_manager.signal(server_event.PlaySequenceEvent(id))
        return Response('', 204)

    return app
