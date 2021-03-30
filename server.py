import json
import datetime
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

import base64
from io import BytesIO
#import matplotlib.pyplot as Plt
from matplotlib.figure import Figure

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

@app.route('/plot/<number>/<station_id>/<parameter>', methods=['GET'])
def query_selection(number, station_id, parameter):
    count = (Sensor_data.objects(station_id=station_id, parameter=parameter).count())
    print(count)
    start = count - int(number)
    if start < 0:
        start = 0
    selection = Sensor_data.objects(station_id=station_id, parameter=parameter).only("sample_id", "parameter", "time_for", "value", "units")[start:count]
    
    if not selection():  
        result = {"ERROR" : {"STATION" : station_id, "PARAMETER" : parameter}}
        return jsonify(result)
    else:
        xas  = []
        yas  = []
        yas1 = []
        yas2 = []
        keys = list(selection()[0].to_json()["value"].keys())
        units     = selection()[0].to_json()["units"]

        for n in range(len(selection())):
            xas.append(selection()[n].to_json()["time_for"])
            if len(keys) == 1:
                yas.append(selection()[n].to_json()["value"][keys[0]])
            if len(keys) == 3:
                yas.append(selection()[n].to_json()["value"][keys[0]])
                yas1.append(selection()[n].to_json()["value"][keys[1]])
                yas2.append(selection()[n].to_json()["value"][keys[2]])
        
        fig = Figure()
        fig.set_figwidth(20)

        ax = fig.subplots()
        _label = keys[0] + "[" + units +"]"
        ax.plot(xas, yas, lw=2, color="red", label=_label)
        if len(keys) > 1:
            _label = keys[1] + "[" + units +"]"
            ax.plot(xas, yas1, lw=2, color="green", label=_label)
        if len(keys) > 2:
            _label = keys[2] + "[" + units +"]"
            ax.plot(xas, yas2, lw=2, color="blue", label=_label)
        ax.grid()
        ax.legend()
        ax.set_ylabel(parameter)
        
    
        #ax.xticks(rotation=70)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        
        return f"<img src='data:image/png;base64,{data}'/>"
        
        #return jsonify(selection()[5].to_json())


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

