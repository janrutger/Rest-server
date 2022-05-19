google.charts.load('current', {'packages':['line']});



function refresh(parm_id){
    console.log("Func refresh")
    console.log(parm_id)
    if (parm_id == 0){
        url = "http://rest:5000/slice/json/now/170/5/BSEC-Meetstation/co2"
    } else if (parm_id == 1){
        url = "http://rest:5000/slice/json/now/170/5/BSEC-Meetstation/iaq"
    } else if (parm_id == 2){
        url = "http://rest:5000/slice/json/now/170/5/BSEC-Meetstation/voc"
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
    } else if (parm_id == 2){
        document.getElementById("stationName").innerHTML=_stationName
        document.getElementById("parmName2").innerHTML=_parmName
        document.getElementById("parmValue2").innerHTML=_value
        document.getElementById("parmMean2").innerHTML=_parmMean
        document.getElementById("parmMarker2").innerHTML=_marker
    }
    
    google.charts.setOnLoadCallback(plot(info, parm_id));
}

function plot(info, parm_id){
    console.log("Func plot")
    console.log(parm_id)

    //JR Code
    
    parm = Object.keys(info["VALUE_LAST"])[0]
    
    //merge 2x1D to 1x2D array
    var xas = info["TIME_LABELS"];
    var yas = info["VALUE_LIST"][parm];
    var resultArr = [];

    for (let i = 0; i < xas.length; i++) {
        resultArr.push([new Date(xas[i]), yas[i]]);
    };

    
    /*console.log(new Intl.DateTimeFormat('nl', { dateStyle: 'full', timeStyle: 'long' }).format(info["LAST_TIME_FOR"])); */

    //Google Code

    var data = new google.visualization.DataTable();
    data.addColumn('datetime');
    data.addColumn('number', info["PARAMETER"]);

    data.addRows(resultArr)

    lastDate = new Date (info["LAST_TIME_FOR"])
    var options = { weekday: 'long', hour: 'numeric', minute: 'numeric', hour12: false };
    lastDate = new Intl.DateTimeFormat('en-NL', options).format(lastDate);
  

    var options = {
        title: info["PARAMETER"] + " - " + parm + "[" + info["UNITS"] + "]",
        subtitle: lastDate,
        width: 840,
        height: 210,
        hAxis: {
            format: 'EEE'
        },
        legend: {position: 'none', textStyle: {color: 'red', fontSize: 16}}
    };

    if (parm_id == 0){
        var chart = new google.charts.Line(document.getElementById('PlotGraph'));
    } else if (parm_id ==1){
        var chart = new google.charts.Line(document.getElementById('PlotGraph1'));
    } else if (parm_id ==2){
        var chart = new google.charts.Line(document.getElementById('PlotGraph2'));
    }

    chart.draw(data, google.charts.Line.convertOptions(options));
}

function refreshButton(num){
    refresh(num)
}

refresh(0); 
refresh(1);
refresh(2);

refreshTimer = setInterval(function() {refresh(2);
                                refresh(1);
                                refresh(0);}, 450000);
