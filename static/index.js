google.charts.load('current', {'packages':['line']});



function refresh(){
    console.log("Func refresh")
    let url = "http://rest:5000/slice/json/now/36/5/Amsterdam/temperature"
    //let url = "ServerResponse.json"

    fetch(url)
    .then(res => res.json())
    .then(j => {console.log(j)
        return j})
    .then(j => update(j["ANSWER"]) );
    
}   

function update(info){
    console.log("Func update")
    console.log(info)

    parm = Object.keys(info["VALUE_LAST"])[0]
    value  = info["VALUE_LAST"][parm]
    markerValue = info["VALUE_N_AVERAGE"][parm]

    if (markerValue < value){
        marker = "Higher"
    } else if (markerValue > value){
        marker = "Lower"
    } else {
        marker = "Same"
    }
   
    document.getElementById("stationName").innerHTML=info["STATION"]
    document.getElementById("parmName").innerHTML=info["PARAMETER"].toUpperCase()
    document.getElementById("parmValue").innerHTML=value
    document.getElementById("parmMean").innerHTML=info["VALUE_AVERAGE"][parm]
    document.getElementById("parmMarker").innerHTML=marker

    //plot(info["TIME_LABELS"], info["VALUE_LIST"][parm])

    google.charts.setOnLoadCallback(plot(info));
}

function plot(info){
    console.log("Func plot")
    console.log(info)

    //JR Code
    
    parm = Object.keys(info["VALUE_LAST"])[0]
    markerValue = info["VALUE_N_AVERAGE"][parm]
    if (markerValue < value){
        marker = "Higher"
    } else if (markerValue > value){
        marker = "Lower"
    } else {
        marker = "Same"
    }
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
        width: 1200,
        height: 480
      };

      var chart = new google.charts.Line(document.getElementById('PlotGraph'));

      chart.draw(data, google.charts.Line.convertOptions(options));


}

function refreshButton(){
    refresh()
}