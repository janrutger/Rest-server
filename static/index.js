google.charts.load('current', {'packages':['line']});



function refresh(parm_id){
    console.log("Func refresh")
    console.log(parm_id)
    if (parm_id == 0){
        url = "http://rest:5000/slice/json/today/36/5/Amsterdam/Humidity"
    } else if (parm_id == 1){
        url = "http://rest:5000/slice/json/today/36/5/Amsterdam/temperature"
    } else {
        url = "http://rest:5000/slice/json/today/36/5/Amsterdam/pressure"
    }

    fetch(url)
    .then(res => res.json())
    .then(j => {console.log(j)
        return j})
    .then(j => update(j["ANSWER"], parm_id) );
    
}   

function update(info, parm_id){
    console.log("Func update")
    console.log(parm_id)
    console.log(info)

    parm = Object.keys(info["VALUE_LAST"])[0]
    markerValue = info["VALUE_N_AVERAGE"][parm]

    _stationName = info["STATION"]
    _parmName    = info["PARAMETER"].toUpperCase()
    _value       = info["VALUE_LAST"][parm]
    _parmMean    = info["VALUE_AVERAGE"][parm]

    if (markerValue < _value){
        _marker = "Higher"
    } else if (markerValue > _value){
        _marker = "Lower"
    } else {
        _marker = "Same"
    }
    if (parm_id == 0){
        document.getElementById("stationName").innerHTML=_stationName
        document.getElementById("parmName").innerHTML=_parmName
        document.getElementById("parmValue").innerHTML=_value
        document.getElementById("parmMean").innerHTML=_parmMean
        document.getElementById("parmMarker").innerHTML=_marker
    } else if (parm_id == 1){
        document.getElementById("stationName").innerHTML=_stationName
        document.getElementById("parmName1").innerHTML=_parmName
        document.getElementById("parmValue1").innerHTML=_value
        document.getElementById("parmMean1").innerHTML=_parmMean
        document.getElementById("parmMarker1").innerHTML=_marker
    }
    
    google.charts.setOnLoadCallback(plot(info, parm_id));
}

function plot(info, parm_id){
    console.log("Func plot")
    console.log(info)

    //JR Code
    
    parm = Object.keys(info["VALUE_LAST"])[0]
    /*markerValue = info["VALUE_N_AVERAGE"][parm]
    if (markerValue < value){
        marker = "Higher"
    } else if (markerValue > value){
        marker = "Lower"
    } else {
        marker = "Same"
    }*/

    //merge 2x1D to 1x2D array
    var xas = info["TIME_LABELS"];
    var yas = info["VALUE_LIST"][parm];
    var resultArr = [];

    for (let i = 0; i < xas.length; i++) {
        resultArr.push([new Date(xas[i]), yas[i]]);
    };

    //Google Code

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Sample time');
    data.addColumn('number', info["PARAMETER"]);

      data.addRows(resultArr)

    var options = {
        chart: {
          title: info["PARAMETER"].toUpperCase(),
          subtitle: parm + " " + info["UNITS"]
        },
        width: 830,
        height: 200
    };

    if (parm_id == 0){
        var chart = new google.charts.Line(document.getElementById('PlotGraph'));
    } else if (parm_id ==1){
        var chart = new google.charts.Line(document.getElementById('PlotGraph1'));
    }
    chart.draw(data, google.charts.Line.convertOptions(options));


}

function refreshButton(num){
    refresh(num)
}