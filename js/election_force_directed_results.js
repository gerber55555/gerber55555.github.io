var USER_SPEED = "fast";

var width = 750,
    height = 750,
	padding = 1,
	maxRadius = 3;
	// color = d3.scale.category10();

var sched_objs = [],
	curr_minute = 0;

var act_codes = [
	{"index": "0", "short": "Conservative", "desc": "Conservative"},
	{"index": "1", "short": "Labour", "desc": "Labour"},
	{"index": "2", "short": "Liberal/Liberal Democrats", "desc": "Liberal Democrats"},
	{"index": "3", "short": "Other", "desc": "Other"},
	{"index": "4", "short": "Plaid Cymru/SNP", "desc": "Plaid Cymru/Scottish National Party"},
	{"index": "5", "short": "Did not vote", "desc": "Did not vote"},
];


var speeds = { "slow": 200, "medium": 125, "fast": 75 };


var time_notes = [
	{ "year": "1788", "img": "img/GeorgeWashington.jpg", "color": "yellow", "note": "After the revolutionary war, George Washington is elected as the first president" },
	{ "year": "1792", "img": "img/1922.jpg",  "color": "blue", "note": "" },
	{  "year": "1796", "img": "img/1923.jpg",  "color": "red", "note": "" },
	{  "year": "1800", "img": "img/1924.jpg",  "color": "blue", "note": "" },
	{  "year": "1804", "img": "img/1929.jpg",  "color": "red", "note": "" },
	{  "year": "1808", "img": "img/1931.jpg",  "color": "blue", "note": "" },
	{  "year": "1812", "img": "img/1935.jpg",  "color": "blue", "note": "" },
	{  "year": "1816", "img": "img/1945.jpg",  "color": "red", "note": "" },
	{  "year": "1820", "img": "img/1950.jpg",  "color": "red", "note": "" },
	{  "year": "1824", "img": "img/1951.jpg",  "color": "blue", "note": "" },
	{  "year": "1828", "img": "img/1955.jpg",  "color": "blue", "note": "" },
    {  "year": "1832", "img": "img/1959.jpg",  "color": "blue", "note": "" },
    {  "year": "1836", "img": "img/1964.jpg",  "color": "red", "note": "" },
    {  "year": "1840","img": "img/1966.jpg",  "color": "red", "note": "" },
    {  "year": "1844", "img": "img/1970.jpg",  "color": "blue", "note": "" },
    {  "year": "1848", "img": "img/1974-1.jpg",  "color": "red", "note": "" },
    {  "year": "1852", "img": "img/1974-2.jpg",  "color": "red", "note": "" },
    {  "year": "1856", "img": "img/1979.jpg",  "color": "blue", "note": "" },
    {  "year": "1860", "img": "img/1983.jpg",  "color": "blue", "note": "" },
    {  "year": "1864", "img": "img/1987.jpg",  "color": "blue", "note": "" },
    {  "year": "1868", "img": "img/1992.jpg",  "color": "blue", "note": "" },
    {  "year": "1872", "img": "img/1997.jpg",  "color": "red", "note": "" },
    {  "year": "1876", "img": "img/2001.jpg",  "color": "red", "note": "" },
    {  "year": "1880", "img": "img/2005.jpg",  "color": "red", "note": "" },
    {  "year": "1884", "img": "img/2010.jpg",  "color": "blue", "note": "" },
    {  "year": "1892", "img": "img/2015.jpg",  "color": "blue", "note": "" },
    {  "year": "1896", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1900", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1904", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1908", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1912", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1916", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1920", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1924", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1928", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1932", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1936", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1940", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1944", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1948", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1952", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1956", "img": "img/2017.jpg",  "color": "blue", "note": "" },
    {  "year": "1960", "img": "img/2017.jpg",  "color": "blue", "note": "" },
];
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


// Load data and let's do it.
d3.tsv("data/elec_results.tsv", function(error, data) {

	data.forEach(function(d) {
		var day_array = d.day.split(",");
		var activities = [];
		for (var i=0; i < day_array.length; i++) {
			// Duration
			if (i % 2 == 1) {
				activities.push({'act': day_array[i-1], 'duration': +day_array[i]});
			}
		}
		sched_objs.push(activities);
	});

	// Used for percentages by minute
	var act_counts = { "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0 };

	// A node for each person's schedule
	var nodes = sched_objs.map(function(o,i) {
		var act = o[0].act;
		act_counts[act] += 1;
		var init_x = foci[act].x + Math.random();
		var init_y = foci[act].y + Math.random();
		return {
			act: act,
			radius: 3,
			x: init_x,
			y: init_y,
			color: color(act),
			moves: 0,
			next_move_time: o[0].duration,
			sched: o,
		}
	});

	var force = d3.layout.force()
		.nodes(nodes)
		.size([width, height])
		// .links([])
		.gravity(0)
		.charge(0)
		.friction(.9)
		.on("tick", tick)
		.start();

	var circle = svg.selectAll("circle")
		.data(nodes)
	    .enter().append("circle")
		.attr("r", function(d) { return d.radius; })
		.style("fill", function(d) { return d.color; });
		// .call(force.drag);

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


	// Update nodes based on activity and duration
	function timer() {
		d3.range(nodes.length).map(function(i) {
			var curr_node = nodes[i],
				curr_moves = curr_node.moves;

			// Time to go to next activity
			if (curr_node.next_move_time == curr_minute) {
				if (curr_node.moves == curr_node.sched.length-1) {
					curr_moves = 0;
				} else {
					curr_moves += 1;
				}

				// Subtract from current activity count
				act_counts[curr_node.act] -= 1;

				// Move on to next activity
				curr_node.act = curr_node.sched[ curr_moves ].act;

				// Add to new activity count
				act_counts[curr_node.act] += 1;

				curr_node.moves = curr_moves;
				curr_node.cx = foci[curr_node.act].x;
				curr_node.cy = foci[curr_node.act].y;

				nodes[i].next_move_time += nodes[i].sched[ curr_node.moves ].duration;
			}

		});

		force.resume();
		curr_minute += 1;

		// Update percentages
		label.selectAll("tspan.actpct")
			.text(function(d) {
				return readablePercent(act_counts[d.index]);
			});

		// Update year and notes
		var true_minute = curr_minute % 1440;
		if (true_minute == time_notes[notes_index].start_minute) {
		    d3.select("#year")
		        .style("color", "#fffced")
		        .style("text-align", "left")
		        .style("font-size", "300%")
				.style("font-family", "adobe-caslon-pro")
				.text(time_notes[notes_index].year)
				.transition()
				.duration(500)
				.style("text-align", "center")
				.style("color", "#000000");
		}

        if (true_minute == time_notes[notes_index].start_minute + 10) {
			d3.select("#image").append('img')
			    .attr('src', time_notes[notes_index].img)
                .attr('width', 200)
                .attr('height', 250)
                .style('position', 'absolute')
                .style('top', '100px')
                .style('left', '150px')
                .style('opacity', 0)
                .style("display", "block")
                .style("background", time_notes[notes_index].color)
                .style("padding", "8px")
                .style("border", "1px solid #ccc")
                .style("box-shadow", "5px 5px 5px #999")
                .transition()
                .duration(1000)
                .style('opacity', 1);
	    }

		if (true_minute == time_notes[notes_index].start_minute + 10) {
			d3.select("#note")
				.style("top", "500px")
				.style("color", "#fffced")
				.style("font-size", "150%")
				.style("font-style", "italic")
			    .transition()
				.duration(500)
				.style("top", "370px")
				.style("color", "#000000")
				.text(time_notes[notes_index].note);
	    }

	    if (true_minute == time_notes[notes_index].stop_minute - 5) {
	        d3.select('#image')
	            .transition()
	            .duration(500)
	            .attr('opacity', 0);
	    }

		// Make note disappear at the end.
		else if (true_minute == time_notes[notes_index].stop_minute) {

			d3.select("#note").transition()
				.duration(500)
				.style("top", "500px")
				.style("color", "#fffced");

			d3.select("#year").transition()
				.duration(500)
				.style("top", "300px")
				.style("color", "#fffced");

			notes_index += 1;
			if (notes_index == time_notes.length) {
				notes_index = 0;
			}
		}


		setTimeout(timer, speeds[USER_SPEED]);
	}
	setTimeout(timer, speeds[USER_SPEED]);


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




	// Speed toggle
	d3.selectAll(".togglebutton")
      .on("click", function() {
        if (d3.select(this).attr("data-val") == "slow") {
            d3.select(".slow").classed("current", true);
			d3.select(".medium").classed("current", false);
            d3.select(".fast").classed("current", false);
        } else if (d3.select(this).attr("data-val") == "medium") {
            d3.select(".slow").classed("current", false);
			d3.select(".medium").classed("current", true);
            d3.select(".fast").classed("current", false);
        }
		else {
            d3.select(".slow").classed("current", false);
			d3.select(".medium").classed("current", false);
			d3.select(".fast").classed("current", true);
        }

		USER_SPEED = d3.select(this).attr("data-val");
    });
}); // @end d3.tsv



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