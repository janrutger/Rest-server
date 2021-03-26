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
    return jsonify(sampels().to_json())

@app.route('/plot/<station_id>/<parameter>', methods=['GET'])
def query_selection(station_id, parameter):
    selection = Sensor_data.objects(station_id=station_id, parameter=parameter).only("sample_id", "time_for", "value")[0:5]
    if not selection():  
        result = {"ERROR" : {"STATION" : station_id, "PARAMETER" : parameter}}
        return jsonify(result)
    else:
        xas = []
        yas = []
        for n in range(5):
            xas.append(selection()[n].to_json()["time_for"])
            yas.append(selection()[n].to_json()["value"]["T"])
        
        return jsonify(selection()[5].to_json())


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




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

