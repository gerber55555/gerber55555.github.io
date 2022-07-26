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


// Activity to put in center of circle arrangement
var center_act = "Did not vote",
	center_pt = { "x": 380, "y": 365 };


// Coordinates for activities
var foci = {};
act_codes.forEach(function(code, i) {
	if (code.desc == center_act) {
		foci[code.index] = center_pt;
	} else {
		var theta = 2 * Math.PI / (act_codes.length-1);
		foci[code.index] = {x: 250 * Math.cos((i - 1) * theta)+380, y: 250 * Math.sin((i - 1) * theta)+365 };
	}
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
d3.csv("data/presidential_results.csv", function(data) {
	for(var i = 0; i < data.length; i++) {
		let yearData = {
			"year": data[i].Year,
			"republican": data[i].Republican,
			"democrat": data[i].Democrat,
			"independent": data[i].Independent
		}
		electionData.push(yearData);
	}

	// initialize nodes
	act_counts = { "0": electionData[0].republican * 538, "1": electionData[0].democrat * 538, "2": electionData[0].independent * 538 };

	//Init republican nodes
	for(var i = 0; i < act_counts[0]; i++) {
		var init_x = foci[0].x + Math.random();
		var init_y = foci[0].y + Math.random();
		let node = {
			act: 0,
			radius: 3,
			x: init_x,
			y: init_y,
			color: "red"
		}
		nodes.push(node)
	}
});

var force = d3.layout.force()
		.nodes(nodes)
		.size([width, height])
		// .links([])
		.gravity(0)
		.charge(0)
		.friction(.9)
		.start();

var circle = svg.selectAll("circle")
	.data(nodes)
	.enter().append("circle")
	.attr("r", function(d) { return d.radius; })
	.style("fill", function(d) { return d.color; });

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