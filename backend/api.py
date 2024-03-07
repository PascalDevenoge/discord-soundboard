import functools
import json
import logging
from queue import Empty
from typing import Any
from uuid import UUID

import data_access
from flask import Blueprint
from flask import request
from flask import Response
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate
from jsonschema import ValidationError
from markupsafe import escape
import server_event
from server_event import ClipDeletedEvent
from server_event import ClipUpdatedEvent
from server_event import EventManager
from server_event import SequenceDeletedEvent

log = logging.getLogger('REST API')


def get_bp(db: SQLAlchemy, event_manager: EventManager):
    bp = Blueprint('api', __name__, url_prefix='/api')

    clip_info_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "length": {"type": "integer"},
            "volume": {"type": "number"}
        },
        "required": ["name", "length", "volume"]
    }

    sequence_info_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "length": {"type": "integer"},
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "position": {"type": "integer"},
                        "delay": {"type": "integer"},
                        "volume": {"type": "number"},
                        "clip_id": {
                            "type": "string",
                            "format": "uuid"
                        }
                    },
                    "required": ["position", "delay", "volume", "clip_id"]
                },
                "minItems": 1
            }
        }
    }

    settings_schema = {
        "type": "object",
        "properties": {
            "play_all_count": {"type": "integer"},
            "play_join_clip": {"type": "boolean"},
            "join_clip_is_sequence": {"type": "boolean"},
            "join_clip_id": {
                "type": "string",
                "format": "uuid"
            },
            "target_channel_name": {"type": "string"}
        },
        "required": ["play_all_count", "play_join_clip", "join_clip_is_sequence", "target_channel_name"]
    }

    def parseId(func):
        @functools.wraps(func)
        def wrapper(id: str, *args, **kwargs):
            try:
                uuid = UUID(escape(id))
            except:
                return Response(400, 'Malformed request')
            return func(uuid, *args, **kwargs)
        return wrapper

    def clipMustExist(func):
        @functools.wraps(func)
        def wrapper(id: UUID, *args, **kwargs):
            if not data_access.clip_exists(db.session, id):
                return Response(f'Clip {id} does not exist', 404)
            return func(id, *args, **kwargs)
        return wrapper

    def sequenceMustExist(func):
        @function.wraps(func)
        def wrapper(id: UUID, *args, **kwargs):
            if not data_access.sequence_exists(db.session, id):
                return Response(f'Sequence {id} does not exist', 404)
            return func(id, *args, **kwargs)
        return wrapper

    def jsonValidates(schema: dict):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    validate(request.get_json(cache=True), schema)
                except ValidationError:
                    return Response('Malformed request', 400)

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def parse_to_data_obj(target_class):
        return target_class.from_dict(request.get_json())

    @bp.route('/clips', methods=['GET'])
    def get_clips():
        return {
            clip_info.id: clip_info.to_json(exclude='id')
            for clip_info in data_access.get_all_clip_infos(db.session)}

    @bp.route('/clips', methods=['POST'])
    def create_clip():
        pass

    @bp.route('/clips/<string:id>', methods=['GET'])
    @parseId
    @clipMustExist
    def get_clip_info(id: UUID):
        return Response(data_access.get_clip_info(db.session, id).to_json(exclude=('id',)), 200, mimetype='application/json')

    @bp.route('/clips/<string:id>', methods=['PUT'])
    @parseId
    @clipMustExist
    @jsonValidates(clip_info_schema)
    def set_clip_info(id: UUID):
        clip_info = parse_to_data_obj(data_access.ClipInfo)
        data_access.set_clip_info(db.session, id, clip_info)
        event_manager.signal(ClipUpdatedEvent(id))
        return Response('', 204)

    @bp.route('/clips/<string:id>', methods=['DELETE'])
    @parseId
    @clipMustExist
    def delete_clip(id: UUID):
        try:
            data_access.delete_clip(db.session, id)
        except data_access.ClipStillUsedException as e:
            return Response(f'Clip still in use in sequence {e.sequence_id}', 409)

        event_manager.signal(ClipDeletedEvent(id))
        return Response('', 204)

    @bp.route('/sequences', methods=['GET'])
    def get_sequences():
        return {
            sequence_info.id: sequence_info.to_json(exclude=('id',))
            for sequence_info in data_access.get_all_sequences(db.session)}

    @bp.route('/sequences', methods=['POST'])
    def create_sequence():
        pass

    @bp.route('/sequences/<string:id>', methods=['GET'])
    @parseId
    @sequenceMustExist
    def get_sequence_info(id: UUID):
        return Response(data_access.get_sequence(db.session, id).to_json(exclude=('id',)), 200, mimetype='application/json')

    @bp.route('/sequences/<string:id>', methods=['PUT'])
    @parseId
    @sequenceMustExist
    @jsonValidates(sequence_info_schema)
    def set_sequence_info():
        pass

    @bp.route('/sequences/<string:id>', methods=['DELETE'])
    @parseId
    @sequenceMustExist
    def delete_sequence(id: UUID):
        data_access.delete_sequence(db.session, id)
        event_manager.signal(SequenceDeletedEvent(id))
        return Response('', 204)

    @bp.route('/settings', methods=['GET'])
    def get_settings():
        return Response(data_access.get_global_settings(db.session).to_json(), 200, mimetype='application/json')

    @bp.route('/settings', methods=['PUT'])
    @jsonValidates(settings_schema)
    def store_settings():
        settings = parse_to_data_obj(data_access.GlobalSettings)
        data_access.save_global_settings(db.session, settings)
        return Response('', 204)

    def format_event(event_name: str, payload: dict[str, Any]):
        return f'event: {event_name}\ndata: {json.dumps(payload)}\nretry: 5000\n\n'

    @bp.route('/events', methods=['GET'])
    def listen_events():
        def event_generator():
            try:
                subscription = event_manager.subscribe()

                while True:
                    try:
                        event: server_event.Event = subscription.listen(
                            timeout=20)

                        match event, type:
                            case server_event.EventType.PLAY_CLIP:
                                yield format_event('clip-played', {"id": str(event.id)})
                            case server_event.EventType.PLAY_ALL:
                                yield format_event('all-clips-played', {})
                            case server_event.EventType.STOP_ALL:
                                yield format_event('all-clips-stopped', {})
                            case server_event.EventType.STOP_CLIP:
                                yield format_event('clip-stopped', {'id': str(event.id)})
                            case server_event.EventType.CLIP_UPLOADED:
                                yield format_event('clip-uploaded', {"id": str(event.id), "name": event.name, "length": event.length})
                            case server_event.EventType.CLIP_DELETED:
                                yield format_event('clip-deleted', {"id": str(event.id)})
                            case server_event.EventType.CLIP_UPDATED:
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
                log.info('Connection closed')
        return Response(event_generator(), mimetype='text/event-stream')

    @bp.route('/events', methods=['POST'])
    def signal_event():
        pass

    return bp
