from flask import Blueprint


def get_bp(db):
    bp = Blueprint('api', __name__, url_prefix='/api')

    @bp.route('/clips', methods=['GET'])
    def get_clips():
        pass

    @bp.route('/clips', methods=['POST'])
    def create_clip():
        pass

    @bp.route('/clips/<string:id>', methods=['GET'])
    def get_clip_info():
        pass

    @bp.route('/clips/<string:id>', methods=['PUT'])
    def set_clip_info():
        pass

    @bp.route('/clips/<string:id>', methods=['DELETE'])
    def delete_clip():
        pass

    @bp.route('/sequences', methods=['GET'])
    def get_sequences():
        pass

    @bp.route('/sequences', methods=['POST'])
    def create_sequence():
        pass

    @bp.route('/sequences/<string:id>', methods=['GET'])
    def get_sequence_info():
        pass

    @bp.route('/sequences/<string:id>', methods=['PUT'])
    def set_sequence_info():
        pass

    @bp.route('/sequences/<string:id>', methods=['DELETE'])
    def delete_sequence():
        pass

    @bp.route('/settings', methods=['GET'])
    def get_settings():
        pass

    @bp.route('/settings', methods=['PUT'])
    def store_settings():
        pass

    @bp.route('/events', methods=['GET'])
    def listen_events():
        pass

    @bp.route('/events', methods=['POST'])
    def signal_event():
        pass

    return bp
