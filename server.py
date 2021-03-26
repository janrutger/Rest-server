import json
import datetime
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'SampleData',
    'host': 'ubuntu.home',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

# class User(db.Document):
#     name = db.StringField()
#     email = db.StringField()
#     def to_json(self):
#         return {"name": self.name,
#                 "email": self.email}

class Sensor_data(db.Document):
    sample_id  = db.StringField(primary_key=True)
    time_at    = db.DateTimeField()
    station_id = db.StringField()
    parameter  = db.StringField()
    time_for   = db.DateTimeField()
    value      = db.DictField()
    units      = db.StringField()
    def to_json(self):
        return {"sample_id" : self.sample_id,
                "time_at"   : self.time_at,
                "station_id": self.station_id,
                "parameter" : self.parameter,
                "time_for"  : self.time_for,
                "value"     : self.value,
                "units"     : self.units}
    


@app.route('/', methods=['GET'])
def query_records():
    #sampels = Sensor_data.objects.order_by("-time_for").first()
    sampels = Sensor_data.objects.order_by("-time_for")[0:10]
    # # jr = Sensor_data.objects.order_by("-time_for")[0:2]
    # # print(len(jr))
    # # print(jr.to_json())
    # # print(jr[5].to_json())

    # print(len(sampels()))
    # print(type(sampels()))
    # print(sampels())
    # val = {}
    # for n in range(0, 10):
    #     #print(sampels[n].to_json())
    #     val[n] = sampels[n].to_json()
    # #return jsonify(val)
    return jsonify(sampels().to_json())

@app.route('/plot/<station_id>/<parameter>', methods=['GET'])
def query_selection(station_id, parameter):
    selection = Sensor_data.objects(station_id=station_id, parameter=parameter).only("time_for", "value").first
    if not selection():  
        result = {"ERROR" : {"STATION" : station_id, "PARAMETER" : parameter}}
        return jsonify(result)
    else:
        return jsonify(selection().to_json())

# @app.route('/', methods=['PUT'])
# def create_record():
#     record = json.loads(request.data)
#     user = User(name=record['name'],
#                 email=record['email'])
#     user.save()
#     return jsonify(user.to_json())

@app.route('/', methods=['POST'])
def update_record():
    records = json.loads(request.data)
    for record in records:
        print(record)

        sample = Sensor_data(sample_id =record[0],
                             station_id=record[1],
                             parameter =record[2],
                             time_at =datetime.datetime.strptime(record[3], "%Y-%m-%dT%H:%M:%S"),
                             time_for=datetime.datetime.strptime(record[4], "%Y-%m-%dT%H:%M:%S"),
                             value =record[5],
                             units=record[6])
        
        sample.save()
    return jsonify({"data received" : "ok"})


# @app.route('/', methods=['DELETE'])
# def delete_record():
#     record = json.loads(request.data)
#     user = User.objects(name=record['name']).first()
#     if not user:
#         return jsonify({'error': 'data not found'})
#     else:
#         user.delete()
#     return jsonify(user.to_json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

