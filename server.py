import json
from datetime import datetime
from datetime import timedelta
from flask import Flask, request, jsonify, make_response
from flask_mongoengine import MongoEngine

import base64
from io import BytesIO
#import matplotlib.pyplot as Plt
from matplotlib.figure import Figure

import statistics as stats

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

@app.route('/slice/<output>/<endtime>/<hours>/<marker>/<station_id>/<parameter>', methods=['GET'])
def query_slice(output, endtime, hours, marker, station_id, parameter):
    print("check Time Fields")
    if endtime == "now":
        end = datetime.now()
    elif endtime == "today":
        end_ = datetime.now()
        end_ = end_.strftime("%Y%m%d2359")
        end = datetime.strptime(end_, '%Y%m%d%H%M')
    elif len(endtime) == 8:
        end = datetime.strptime(endtime, '%Y%m%d')
    elif len(endtime) == 12:
        end = datetime.strptime(endtime, '%Y%m%d%H%M')
    else:
        result = {"ERROR" : {"wrong date" : endtime}}
        return jsonify(result)

    start = end - timedelta(hours=int(hours))
    print("Start query")
    selection = Sensor_data.objects(station_id=station_id, parameter=parameter, time_for__gte=start, time_for__lte=end)

    if not selection():
        result = {"ERROR" : {"OUTPUT"    : output,
                             "STARTTIME" : endtime,
                             "HOURS"     : hours,
                             "STATION"   : station_id,
                             "PARAMETER" : parameter}
        }
        return jsonify(result)
    else:
        print("Proces result")
        xas = []
        yas = []
        yas1= []
        yas2= []
        lastNvalues = []
        lastNvalues1= []
        lastNvalues2= []
        parmKeys = list(selection()[0].to_json()["value"].keys())
        parmUnits     = selection()[0].to_json()["units"]

        #lastRecord = selection.order_by("-time_for").first()

        reverse_selection = selection.order_by("-time_for")
        lastRecord  = reverse_selection[0]

        if len(reverse_selection) < int(marker):
            marker = len(reverse_selection)
        if len(parmKeys) == 1:
            for n in range(0, int(marker)):
                lastNvalues.append(reverse_selection[n].to_json()["value"][parmKeys[0]])
        if len(parmKeys) == 3:
            for n in range(0, int(marker)):
                lastNvalues.append(reverse_selection[n].to_json()["value"][parmKeys[0]])
                lastNvalues1.append(reverse_selection[n].to_json()["value"][parmKeys[1]])
                lastNvalues2.append(reverse_selection[n].to_json()["value"][parmKeys[2]])


        for n in range(len(selection())):
            xas.append((selection()[n].to_json()["time_for"]))
            if len(parmKeys) == 1:
                yas.append(selection()[n].to_json()["value"][parmKeys[0]])
            if len(parmKeys) == 3:
                yas.append(selection()[n].to_json()["value"][parmKeys[0]])
                yas1.append(selection()[n].to_json()["value"][parmKeys[1]])
                yas2.append(selection()[n].to_json()["value"][parmKeys[2]])
        
        
        print("Make JSON")
        if len(parmKeys) == 1:
            result = {"ANSWER" : {"VALUE_LAST" : {parmKeys[0] : lastRecord.value[parmKeys[0]]},
                                      "VALUE_AVERAGE" : {parmKeys[0] : stats.mean(yas)},
                                      "VALUE_N_AVERAGE" : {parmKeys[0] : stats.mean(lastNvalues)},
                                      "VALUE_MEDIAN"  : {parmKeys[0] : stats.median(yas)},
                                      "UNITS"     : parmUnits,
                                      "LAST_TIME_FOR" : lastRecord.time_for,
                                      "LAST_TIME_AT"  : lastRecord.time_at,
                                      "LAST_TIME_QUERY" : end,
                                      "STATION"   : station_id,
                                      "PARAMETER" : parameter,
                                      "SLICE_LEN" : len(xas),
                                      "TIME_LABELS" : xas, 
                                      "VALUE_LIST"  : {parmKeys[0] : yas}
                                            }}
                
        if len(parmKeys) == 3:
            result = {"ANSWER" : {"VALUE_LAST" : {parmKeys[0] : lastRecord.value[parmKeys[0]], 
                                                parmKeys[1] : lastRecord.value[parmKeys[1]], 
                                                parmKeys[2] : lastRecord.value[parmKeys[2]] },
                                      "VALUE_AVERAGE" : {parmKeys[0] : stats.mean(yas), 
                                                parmKeys[1] : stats.mean(yas1), 
                                                parmKeys[2] : stats.mean(yas2) },
                                      "VALUE_N_AVERAGE" : {parmKeys[0] : stats.mean(lastNvalues), 
                                                parmKeys[1] : stats.mean(lastNvalues1), 
                                                parmKeys[2] : stats.mean(lastNvalues2) },                                        
                                      "VALUE_MEDIAN"  : {parmKeys[0] : stats.median(yas), 
                                                   parmKeys[1] : stats.median(yas1), 
                                                   parmKeys[2] : stats.median(yas2) },
                                      "UNITS"     : parmUnits,
                                      "LAST_TIME_FOR" : lastRecord.time_for,
                                      "LAST_TIME_AT"  : lastRecord.time_at,
                                      "STATION"   : station_id,
                                      "PARAMETER" : parameter,
                                      "SLICE_LEN" : len(xas),
                                      "TIME_LABELS" : xas, 
                                      "VALUE_LIST"  : {parmKeys[0] : yas, 
                                                    parmKeys[1] : yas1, 
                                                    parmKeys[2] : yas2 }
                                            }}

        if output == "json":
            print("return JSON")
            response = make_response(jsonify(result))
            response.headers["Content-Type"] = "application/json"
            print(response.headers)
            print(response.data)
            return(response)
            #return(jsonify(result))


        elif output == "plot":
            print("Compose plot")
            fig = Figure()
            fig.set_figwidth(20)
            ax = fig.subplots()

            parm_Keys = list(result["ANSWER"]["VALUE_LAST"].keys())

            if len(result["ANSWER"]["VALUE_LAST"]) == 1:
                _Label = parm_Keys[0] + "[" + result["ANSWER"]["UNITS"] + "]"
                if result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] > result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "v"
                elif result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] < result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "^"
                else:
                    _marker = "d"

                ax.plot(result["ANSWER"]["TIME_LABELS"],  result["ANSWER"]["VALUE_LIST"][parm_Keys[0]],                                      lw=1, color="red", marker=_marker, label=_Label )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_AVERAGE"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],    lw=1, color="red", linestyle="dotted" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_MEDIAN"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],     lw=1, color="red", linestyle="dashed" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],  lw=1, color="red", linestyle="dashdot" )
            if len(result["ANSWER"]["VALUE_LAST"]) == 3:
                _Label = parm_Keys[0] + "[" + result["ANSWER"]["UNITS"] + "]"
                if result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] > result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "v"
                elif result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] < result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "^"
                else:
                    _marker = "d"
                ax.plot(result["ANSWER"]["TIME_LABELS"],  result["ANSWER"]["VALUE_LIST"][parm_Keys[0]],                                      lw=1, color="red", marker=_marker, label=_Label )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_AVERAGE"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],    lw=1, color="red", linestyle="dotted" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_MEDIAN"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],     lw=1, color="red", linestyle="dashed" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]]]*result["ANSWER"]["SLICE_LEN"],  lw=1, color="red", linestyle="dashdot" )

                
                
                _Label = parm_Keys[1] + "[" + result["ANSWER"]["UNITS"] + "]"
                if result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] > result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "v"
                elif result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] < result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "^"
                else:
                    _marker = "d"
                ax.plot(result["ANSWER"]["TIME_LABELS"],  result["ANSWER"]["VALUE_LIST"][parm_Keys[1]],                                      lw=1, color="green", marker=_marker, label=_Label )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_AVERAGE"][parm_Keys[1]]]*result["ANSWER"]["SLICE_LEN"],    lw=1, color="green", linestyle="dotted" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_MEDIAN"][parm_Keys[1]]]*result["ANSWER"]["SLICE_LEN"],     lw=1, color="green", linestyle="dashed" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[1]]]*result["ANSWER"]["SLICE_LEN"],  lw=1, color="green", linestyle="dashdot" )

                
                
                _Label = parm_Keys[2] + "[" + result["ANSWER"]["UNITS"] + "]"
                if result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] > result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "v"
                elif result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[0]] < result["ANSWER"]["VALUE_LAST"][parm_Keys[0]]:
                    _marker = "^"
                else:
                    _marker = "d"
                ax.plot(result["ANSWER"]["TIME_LABELS"],  result["ANSWER"]["VALUE_LIST"][parm_Keys[2]],                                      lw=1, color="blue", marker=_marker, label=_Label )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_AVERAGE"][parm_Keys[2]]]*result["ANSWER"]["SLICE_LEN"],    lw=1, color="blue", linestyle="dotted" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_MEDIAN"][parm_Keys[2]]]*result["ANSWER"]["SLICE_LEN"],     lw=1, color="blue", linestyle="dashed" )
                ax.plot(result["ANSWER"]["TIME_LABELS"], [result["ANSWER"]["VALUE_N_AVERAGE"][parm_Keys[2]]]*result["ANSWER"]["SLICE_LEN"],  lw=1, color="blue", linestyle="dashdot" )
            
            ax.grid()
            ax.legend()
            ax.set_ylabel(parameter)
        
            print("Render PNG")
            #ax.xticks(rotation=70)
            # Save it to a temporary buffer.
            buf = BytesIO()
            fig.savefig(buf, format="png")
            # Embed the result in the html output.
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            print("Send PNG")
            return f"<img src='data:image/png;base64,{data}'/>"


@app.route('/plot/<hours>/<station_id>/<parameter>', methods=['GET'])
def query_selection(hours, station_id, parameter):
    # count = (Sensor_data.objects(station_id=station_id, parameter=parameter).count())
    # print(count)
    # start = count - int(number)
    # if start < 0:
    #     start = 0
    # selection = Sensor_data.objects(station_id=station_id, parameter=parameter).only("sample_id", "parameter", "time_for", "value", "units")[start:count]

    startdate = datetime.now() - timedelta(hours=int(hours))
    selection = Sensor_data.objects(station_id=station_id, parameter=parameter, time_for__gte=startdate)
    print(len(selection))
    
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
        ax.plot(xas, yas, lw=1, color="red", marker="d", label=_label)
        if len(keys) > 1:
            _label = keys[1] + "[" + units +"]"
            ax.plot(xas, yas1, lw=1, color="green", marker="^", label=_label)
        if len(keys) > 2:
            _label = keys[2] + "[" + units +"]"
            ax.plot(xas, yas2, lw=1, color="blue",marker="v",  label=_label)
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

                             time_at =datetime.strptime(record[3], "%Y-%m-%dT%H:%M:%S"),
                             time_for=datetime.strptime(record[4], "%Y-%m-%dT%H:%M:%S"),
                             value =record[5],
                             units=record[6])
        
        sample.save()
    return jsonify({"data received" : "ok"})




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

