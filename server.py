import json
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'your_database',
    'host': 'ubuntu.home',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    def to_json(self):
        return {"name": self.name,
                "email": self.email}

class Sensor_data(db.Document):
    sample_id  = db.StringField()
    time_at    = db.DateTimeField()
    station_id = db.StringField()
    parameter  = db.StringField()
    time_for   = db.DateTimeField()
    value      = db.DictField()
    units      = db.StringField()
    def to_json(self):
        return {"sample_is" : self.sample_id,
                "time_at"   : self.time_at,
                "station_id": self.station_id,
                "parameter" : self.parameter,
                "time_for"  : self.time_for,
                "value"     : self.value,
                "units"     : self.units}
    


@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    user = User.objects(name=name).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(user.to_json())

@app.route('/', methods=['PUT'])
def create_record():
    record = json.loads(request.data)
    user = User(name=record['name'],
                email=record['email'])
    user.save()
    return jsonify(user.to_json())

@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    print(record)
    print(type(record[0]))
    # user = User.objects(name=record['name']).first()
    # if not user:
    #     return jsonify({'error': 'data not found'})
    # else:
    #     user.update(email=record['email'])
    # return jsonify(user.to_json())
    return jsonify({"data received" : "ok"})


@app.route('/', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    user = User.objects(name=record['name']).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        user.delete()
    return jsonify(user.to_json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

