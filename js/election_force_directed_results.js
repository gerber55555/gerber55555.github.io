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

var center_act = "Independent",
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
var force; 
var circle;
var sched_objs = [];
d3.csv("data/presdential_results.csv", function(data) {
	for(var i = 0; i < data.length; i++) {
		var republican = data[i].r;
		var democrat = data[i].d;
		var independent = data[i].i;
		for(var j = 0; j < 538; j++) {
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
	var act_counts = { "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0 };

	var nodes = sched_objs.map(function(o,i) {
		var act = o[0];
		act_counts[act] += 1;
		var init_x = foci[act].x + Math.random();
		var init_y = foci[act].y + Math.random();
		return {
			act: act,
			radius: 6,
			x: init_x,
			y: init_y,
			color: color(act),
			moves: 0,
			sched: o,
		}
	});

	force = d3.layout.force()
		.nodes(nodes)
		.size([width, height])
		// .links([])
		.gravity(0)
		.charge(0)
		.friction(.9)
		.on("tick", tick)
		.start();
	
	circle = svg.selectAll("circle")
	.data(nodes)
	.enter().append("circle")
	.attr("r", function(d) { return d.radius; })
	.style("fill", function(d) { return d.color; });

	// Activity labels
	var label = svg.selectAll("text")
		.data(act_codes)
	  .enter().append("text")
		.attr("class", "actlabel")
		.attr("x", function(d, i) {
			if (d.desc == center_act) {
				return center_pt.x;
			} else {
				var theta = 2 * Math.PI / (act_codes.length-1);
				return 340 * Math.cos((i - 1) * theta)+380;
			}
		})
		.attr("y", function(d, i) {
			if (d.desc == center_act) {
				return center_pt.y;
			} else {
				var theta = 2 * Math.PI / (act_codes.length-1);
				return 340 * Math.sin((i - 1) * theta)+365;
			}
		});

	label.append("tspan")
		.attr("x", function() { return d3.select(this.parentNode).attr("x"); })
		// .attr("dy", "1.3em")
		.attr("text-anchor", "middle")
		.text(function(d) {
			return d.short;
		});
	label.append("tspan")
		.attr("dy", "1.3em")
		.attr("x", function() { return d3.select(this.parentNode).attr("x"); })
		.attr("text-anchor", "middle")
		.attr("class", "actpct")
		.text(function(d) {
			return act_counts[d.index] + "%";
		});

	d3.selectAll(".nextbutton").on("click", function() {
		if(curr_slide < data.length) {
			curr_slide += 1;
			d3.range(nodes.length).map(function(i) {
				var current_node = nodes[i];
				act_counts[current_node.act] -= 1;
				current_node.act = current_node.sched[curr_slide];
				act_counts[current_node.act] += 1;
				current_node.cx = foci[current_node.act].x;
				current_node.cy = foci[current_node.act].y;
			})
			force.resume();

			// Update percentages
			label.selectAll("tspan.actpct")
			.text(function(d) {
				return readablePercent(act_counts[d.index]);
			});
		}
	});

	d3.selectAll(".prevbutton").on("click", function() {
		if(curr_slide < data.length) {
			curr_slide += 1;
			d3.range(nodes.length).map(function(i) {
				var current_node = nodes[i];
				act_counts[current_node.act] -= 1;
				current_node.act = current_node.sched[curr_slide];
				act_counts[current_node.act] += 1;
				current_node.cx = foci[current_node.act].x;
				current_node.cy = foci[current_node.act].y;
			})
			force.resume();

			// Update percentages
			label.selectAll("tspan.actpct")
			.text(function(d) {
				return readablePercent(act_counts[d.index]);
			});
		}
	})

	function tick(e) {
		var k = 0.04 * e.alpha;
	
		// Push nodes toward their designated focus.
		nodes.forEach(function(o, i) {
			var curr_act = o.act;
			var damper = 1;
			o.color = color(curr_act);
			o.y += (foci[curr_act].y - o.y) * k * damper;
			o.x += (foci[curr_act].x - o.x) * k * damper;
		});
	
		circle
				.each(collide(.5))
				.style("fill", function(d) { return d.color; })
			.attr("cx", function(d) { return d.x; })
			.attr("cy", function(d) { return d.y; });
		}
	
	
		// Resolve collisions between nodes.
		function collide(alpha) {
		var quadtree = d3.geom.quadtree(nodes);
		return function(d) {
			var r = d.radius + maxRadius + padding,
				nx1 = d.x - r,
				nx2 = d.x + r,
				ny1 = d.y - r,
				ny2 = d.y + r;
			quadtree.visit(function(quad, x1, y1, x2, y2) {
			if (quad.point && (quad.point !== d)) {
				var x = d.x - quad.point.x,
					y = d.y - quad.point.y,
					l = Math.sqrt(x * x + y * y),
					r = d.radius + quad.point.radius + (d.act !== quad.point.act) * padding;
				if (l < r) {
				l = (l - r) / l * alpha;
				d.x -= x *= l;
				d.y -= y *= l;
				quad.point.x += x;
				quad.point.y += y;
				}
			}
			return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
			});
		};
		  }
});



function color(activity) {

	var colorByActivity = {
		"0": "blue",
		"1": "red",
		"2": "yellow"
	}

	return colorByActivity[activity];

}


// Output readable percent based on count.
function readablePercent(n) {

	var pct = 100 * n / 1000
	;
	if (pct < 1 && pct > 0) {
		pct = "<1%";
	} else {
		pct = Math.round(pct) + "%";
	}

	return pct;
}