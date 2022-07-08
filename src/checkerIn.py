from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import CheckerIn, db
from flasgger import swag_from
from datetime import datetime
from datetime import timedelta
from datetime import timezone

checkerIn = Blueprint("checkerIn", __name__, url_prefix="/api/v1/checkerin")


@checkerIn.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_checkerIn():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        practiceRecord_data = request.get_json()
        is_checkIn = request.get_json().get('is_checkIn', '')
        checkIn_time = datetime.now(timezone.utc)
        
        checkersIn = CheckerIn(is_checkIn=is_checkIn, checkIn_time=checkIn_time, user_id=current_user)
        db.session.add(checkersIn)
        db.session.commit()

        return jsonify({
            'id': checkersIn.id,
            'is_checkIn': checkersIn.is_checkIn,
            'is_checkOut': checkersIn.is_checkOut,
            'checkIn_time': checkersIn.checkIn_time,
            'checkOut_time': checkersIn.checkOut_time,
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        checkerIn = CheckerIn.query.filter_by(
            user_id=current_user).paginate()

        data = []

        for checkersIn in checkerIn.items:
            data.append({
            'id': checkersIn.id,
            'is_checkIn': checkersIn.is_checkIn,
            'is_checkOut': checkersIn.is_checkOut,
            'checkIn_time': checkersIn.checkIn_time,
            'checkOut_time': checkersIn.checkOut_time,
            })

       

        return jsonify({'data': data}), HTTP_200_OK

@checkerIn.put('/<int:id>')
@checkerIn.patch('/<int:id>')
@jwt_required()
def editcheckerIn(id):
    current_user = get_jwt_identity()

    checkersIn = CheckerIn.query.filter_by(user_id=current_user, id=id).first()

    if not checkersIn:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    
    is_checkOut = request.get_json().get('is_checkOut', '')
    checkOut_time = datetime.now(timezone.utc)

    checkersIn.is_checkOut = is_checkOut
    checkersIn.checkOut_time = checkOut_time
    

    db.session.commit()

    return jsonify({
            'id': checkersIn.id,
            'is_checkIn': checkersIn.is_checkIn,
            'is_checkOut': checkersIn.is_checkOut,
            'checkIn_time': checkersIn.checkIn_time,
            'checkOut_time': checkersIn.checkOut_time,
    }), HTTP_200_OK

@checkerIn.get("/<int:id>")
@jwt_required()
def get_checkerIn(id):
    current_user = get_jwt_identity()

    checkersIn = CheckerIn.query.filter_by(user_id=current_user, id=id).first()

    if not checkersIn:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
            'id': checkersIn.id,
            'is_checkIn': checkersIn.is_checkIn,
            'is_checkOut': checkersIn.is_checkOut,
            'checkIn_time': checkersIn.checkIn_time,
            'checkOut_time': checkersIn.checkOut_time,
    }), HTTP_200_OK