var USER_SPEED = "fast";

var width = 750,
    height = 750,
	padding = 1,
	maxRadius = 3;
	// color = d3.scale.category10();

var sched_objs = [],
	curr_slide = 0;

var act_codes = [
	{"index": "0", "short": "Republican", "desc": "Republican"},
	{"index": "1", "short": "Democrat", "desc": "Democrat"},
	{"index": "2", "short": "Independent", "desc": "Independent"}
];


var speeds = { "slow": 200, "medium": 125, "fast": 75 };


var notes_index = 0;


// Coordinates for activities
var foci = {};
act_codes.forEach(function(code, i) {
	var theta = 2 * Math.PI / (act_codes.length-1);
	foci[code.index] = {x: 250 * Math.cos((i - 1) * theta)+380, y: 250 * Math.sin((i - 1) * theta)+365 };
});


// Start the SVG
var svg = d3.select("#chart").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr('position', 'absolute')
    .attr('left', '200px')
    .attr('top', '200px');


let electionData = [];
var nodes = [];
var act_counts = {};
var force; 
var circle;
var sched_objs = [];
d3.csv("data/presdential_results.csv", function(data) {
	for(var i = 0; i < data.length; i++) {
		var republican = data[i].Republican;
		var democrat = data[i].Democrat;
		var independent = data[i].Independent;
		for(var j = 0; j < 538; i++) {
			if(republican > 0) {
				if(i == 0) {
					sched_objs.push([0])
				} else {
					sched_objs[j].push(0);
				}
				republican -= 1;
			} else if(democrat > 0) {
				if(i == 0) {
					sched_objs.push([1])
				} else {
					sched_objs[j].push(1);
				}
				democrat -= 1;
			} else if(independent > 0) {
				if(i == 0) {
					sched_objs.push([2])
				} else {
					sched_objs[j].push(2);
				}
				independent -= 1;
			} else {
				console.log("You messed up homie");
			}
		}
		console.log("yay")
	}


	force = d3.layout.force()
		.nodes(nodes)
		.size([width, height])
		// .links([])
		.gravity(0)
		.charge(0)
		.friction(.9)
		.start();
	
	circle = svg.selectAll("circle")
	.data(nodes)
	.enter().append("circle")
	.attr("r", function(d) { return d.radius; })
	.style("fill", function(d) { return d.color; });
});



function color(activity) {

	var colorByActivity = {
		"0": "blue",
		"1": "red",
		"2": "yellow",
		"3": "brown",
		"4": "black",
		"5": "grey",
	}

	return colorByActivity[activity];

}



// Output readable percent based on count.
function readablePercent(n) {

	var pct = 100 * n / 1000;
	if (pct < 1 && pct > 0) {
		pct = "<1%";
	} else {
		pct = Math.round(pct) + "%";
	}

	return pct;
}