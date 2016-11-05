function SetUpTabbar() {
  d3.json("/games", function(game_ids) {
      for (var i = 0; i < game_ids.length; i++) {
        var game_id = game_ids[i]["gameid"];

        descriptions[game_id] = game_ids[i]["desc"];
        states[game_id] = game_ids[i]["state"];
        var li = d3.select("#tabbar")
                    .append("li")
                      .attr("role", "presentation")
                      .attr("game_id", game_id)
                      .on("click", function(){
                        d3.select("li.active").attr("class", "");
                        d3.select(this).attr("class", "active");
                        DisplayGame(d3.select(this).attr("game_id"))
                      });
        li.append("a").html(game_ids[i]["desc"]);
        if (i == 0){
          li.attr("class", "active");
          DisplayGame(game_id);
        }
    }
  });
}

Number.prototype.toQMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var quarter   = Math.floor(sec_num / 720);
    var minutes = Math.floor((sec_num - (quarter * 720)) / 60);
    var seconds = sec_num - (quarter * 720) - (minutes * 60);

    quarter = quarter + 1;
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return 'Q'+quarter+' '+minutes+':'+seconds;
}

function DisplayGame(game_id){

    d3.select("#viz").remove("*");
    d3.select("body").append("div")
      .attr("id", "viz");

    if (states[game_id] == "before") {
      d3.select("#viz")
        .append("p")
          .text("Game hasn't started yet.");
      document.getElementById("loader").style.display = "none";
      return;
    }

    d3.json("/" + game_id, function(data) {
      // instantiate d3plus
      var game_data = data["data"];
      var mirrored_data = [];

      visualization = d3plus.viz()
        .container("#viz")
        .data(game_data)  // data to use with the visualization
        .id("id")
        .type("line")       // visualization type
        .text("desc")       // key to use for display text
        .y("Win Percentage")         // key to use for y-axis
        .y({"range": [0, 1], "label": "Home Team Win Percentage"})
        .x("time")          // key to use for x-axis
        .x({"grid": false, "range": [0, 2880]})
        .title(descriptions[data["gameid"]])
        .format({
          "number": function (number, params) {
            if (params.key == 'time')
              return number.toQMMSS();
            else
              return (100 * number).toFixed(1) + "%";
          }
        })
        .draw()             // finally, draw the visualization!
        document.getElementById("loader").style.display = "none";
    })
}
