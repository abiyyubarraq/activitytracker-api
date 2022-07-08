from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Activity, db
from flasgger import swag_from
from datetime import datetime

activity = Blueprint("activity", __name__, url_prefix="/api/v1/activity")


@activity.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_activity():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        practiceRecord_data = request.get_json()
        task = request.get_json().get('task', '')
        desc = request.get_json().get('desc', '')
        work_time_start = datetime.strptime(practiceRecord_data['work_time_start'], '%Y-%m-%dT%H:%M:%S.%f')
        work_time_end = datetime.strptime(practiceRecord_data['work_time_end'], '%Y-%m-%dT%H:%M:%S.%f')


        activities = Activity(task=task, desc=desc, work_time_start = work_time_start, work_time_end=work_time_end, user_id=current_user)
        db.session.add(activities)
        db.session.commit()

        return jsonify({
            'id': activities.id,
            'task': activities.task,
            'desc': activities.desc,
            'work_time_start': activities. work_time_start,
            'work_time_end': activities.work_time_end,
        }), HTTP_201_CREATED

    else:
        activity = Activity.query.filter_by(
            user_id=current_user).paginate()

        data = []

        for activities in activity.items:
            data.append({
            'id': activities.id,
            'task': activities.task,
            'desc': activities.desc,
            'work_time_start': activities. work_time_start,
            'work_time_end': activities.work_time_end,
            })

        return jsonify({'data': data}), HTTP_200_OK


@activity.get("/<int:id>")
@jwt_required()
def get_activities(id):
    current_user = get_jwt_identity()

    activities = Activity.query.filter_by(user_id=current_user, id=id).first()

    if not activities:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
            'id': activities.id,
            'task': activities.task,
            'desc': activities.desc,
            'work_time_start': activities. work_time_start,
            'work_time_end': activities.work_time_end,
    }), HTTP_200_OK


@activity.delete("/<int:id>")
@jwt_required()
def delete_activities(id):
    current_user = get_jwt_identity()

    activities = Activity.query.filter_by(user_id=current_user, id=id).first()

    if not activities:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(activities)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@activity.put('/<int:id>')
@activity.patch('/<int:id>')
@jwt_required()
def editactivities(id):
    current_user = get_jwt_identity()

    activities = Activity.query.filter_by(user_id=current_user, id=id).first()

    if not activities:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    practiceRecord_data = request.get_json()
    task = request.get_json().get('task', '')
    desc = request.get_json().get('desc', '')
    work_time_start = datetime.strptime(practiceRecord_data['work_time_start'], '%Y-%m-%dT%H:%M:%S.%f')
    work_time_end = datetime.strptime(practiceRecord_data['work_time_end'], '%Y-%m-%dT%H:%M:%S.%f')

    activities.task = task
    activities.desc = desc
    activities.work_time_start = work_time_start
    activities.work_time_end = work_time_end

    db.session.commit()

    return jsonify({
            'id': activities.id,
            'task': activities.task,
            'desc': activities.desc,
            'work_time_start': activities. work_time_start,
            'work_time_end': activities.work_time_end,
    }), HTTP_200_OK


@activity.get("/stats")
@jwt_required()
@swag_from("./docs/activity/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Activity.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)

    return jsonify({'data': data}), 