#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re


def write_numpy_array_html(filename, dataname, colour_palette='blue_gradient', min_max=None, d3js_source_path=None):
    if d3js_source_path is None:
        user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
        for user_path in user_paths:
            if re.search('acidano', user_path):
                d3js_source_path = os.path.join(user_path, 'acidano/visualization/d3.v3.min.js')
                break

    # Colour palette
    if colour_palette == 'blue_gradient':
        colour_list = "['#b3c6ff', '#000000']"
    elif colour_palette == 'rainbow':
        colour_list = "['#2c7bb6', '#00a6ca','#00ccbc','#90eb9d','#ffff8c','#f9d057','#f29e2e','#e76818','#d7191c']"
    elif colour_palette == 'hot':   
        colour_list = "['#0b0000', '#550000', '#9f0000', '#ea0000', '#ff3500', '#ff8000', '#ffca00', '#ffff20', '#ffff8f', '#ffffff',]"
    else:
        raise NameError('Undefined colour palette')

    # Custom min and max Z
    if min_max:
        minZ, maxZ = min_max
        minZ = str(minZ)
        maxZ = str(maxZ)
    else:
        maxZ = """d3.max(data, function(d) {
            return d.z;
        })"""
        minZ = """d3.min(data, function(d) {
            return d.z;
        })"""

    text = """<!DOCTYPE html>
<head>
<meta charset="utf-8">

<!-- D3.js -->
<script src=""" + '"' + d3js_source_path + '"' + """ charset="utf-8"></script>

<!-- Google Font -->
<link href="http://fonts.googleapis.com/css?family=Open+Sans:300,400,700" rel="stylesheet" type="text/css">
<title>Numpy visualization</title>
<style>
    html { font-size: 62.5%; }

    body {
        font-size: 1.6rem;
        font-family: 'Open Sans', sans-serif;
        font-weight: 300;
        text-align: center;
    }

    .title {
      font-size: 2.6rem;
      fill: #4F4F4F;
      font-weight: 300;
      text-anchor: middle;
    }

    // Axis and legend
    .legendTitle {
        text-anchor: middle;
        font-size: 2rem;
        fill: #4F4F4F;
        font-weight: 300;
    }

    .axisLine {
        stroke-width: 0.5;
        stroke: black;
    }

    .axis path,
    .axis line {
        opacity: 0;
        /* Hide axis */
    }

    .axis text {
        font-size: 10px;
    }

    .note_label {
        font-size: 15px;
    }

</style>
</head>
<body>
<svg class="graph"></svg>
<script>

    var dataname = '""" + dataname + """'

    var zoom = d3.behavior.zoom()
        .scaleExtent([1, 10])
        .on("zoom", zoomed);

    var width = window.innerWidth - 20,
        height = window.innerHeight - 20;
    margin = {
            top: 200,
            right: 130,
            bottom: 180,
            left: 130
        };
    // barHeight = (height - margin.top - margin.bottom) / 128;
    // Width scaling
    var W = d3.scale.linear()
        .range([margin.left, width - margin.right]);
    var W_text = d3.scale.linear()
        .range([margin.left + 10, width - margin.right - width/3]);
    var W_dx = d3.scale.linear()
        .range([0, width - margin.right - margin.left]);
    // Heigth scaling
    var H = d3.scale.linear()
        .range([height - margin.top, margin.bottom]);
    var H_text = d3.scale.linear()
        .range([height - margin.top - 10, margin.bottom + 30]);
    var H_dy = d3.scale.linear()
        .range([0, height - margin.top - margin.bottom]);
    // Opacity scaling
    var O = d3.scale.linear()
        .range([0,1]);

    // Graph
    var graph = d3.select(".graph")
        .attr("width", width)
        .attr("height", height)
        .call(zoom);

    // Load data
    var filename = dataname.concat('.csv');
    d3.csv(filename, type, function(data) {
        var maxX = d3.max(data, function(d) {
            return d.x;
        });
        var minX = d3.min(data, function(d) {
            return d.x;
        });
        var maxY = d3.max(data, function(d) {
            return d.y;
        });
        var minY = d3.min(data, function(d) {
            return d.y;
        });
        var maxZ = """ + maxZ + """;
        var minZ = """ + minZ + """;
        var deltaX = maxX - minX + 1
        var deltaY = maxY - minY + 1
        var deltaZ = maxZ - minZ + 1

        W.domain([minX, maxX]);
        W_text.domain([minX, maxX]);
        W_dx.domain([0, deltaX]);
        H.domain([minY, maxY]);
        H_text.domain([minY, maxY]);
        H_dy.domain([0, deltaY]);
        O.domain([minZ - deltaZ/10, maxZ + deltaZ/10])

        //Needed for gradients
        var defs = graph.append("defs");
        var coloursRainbow = """ + colour_list + """;
        var colourRangeRainbow = d3.range(0, 1, 1.0 / (coloursRainbow.length - 1));
        colourRangeRainbow.push(1);

        //Create color gradient
        var colorScaleRainbow = d3.scale.linear()
            .domain(colourRangeRainbow)
            .range(coloursRainbow)
            .interpolate(d3.interpolateHcl);

        //Needed to map the values of the dataset to the color scale
        var colorInterpolateRainbow = d3.scale.linear()
            .domain([minZ, maxZ])
            .range([0,1]);

        //Calculate the gradient
        defs.append("linearGradient")
            .attr("id", "gradient-rainbow-colors")
            .attr("x1", "0%").attr("y1", "0%")
            .attr("x2", "100%").attr("y2", "0%")
            .selectAll("stop")
            .data(coloursRainbow)
            .enter().append("stop")
            .attr("offset", function(d,i) { return i/(coloursRainbow.length-1); })
            .attr("stop-color", function(d) { return d; });

        // Adds X-Axis as a 'g' element
        var xAxis = d3.svg.axis()
            .scale(W)
            .orient("bottom")
            .ticks(20);

        graph.append("g").attr({
            "class": "axis", // Give class so we can style it
            "transform": "translate(" + [0, height - margin.bottom+H_dy(1)/2] + ")", // Translate just moves it down into position (or will be on top)
        }).call(xAxis); // Call the xAxis function on the group

        graph.append("text")
            .attr("class", "legendTitle")
            .attr("x", width-margin.right-30)
            .attr("y", height-margin.bottom+50)
            .text("Time");

        //draw_arrow(graph, margin.left, height-margin.bottom+H_dy(1)/2 , width-margin.right, height-margin.bottom+H_dy(1)/2, "right", "axisLine")

        // Adds Y-Axis as a 'g' element
        var yAxis = d3.svg.axis()
            .scale(H)
            .orient("left")
            .ticks(9);

        graph.append("g").attr({
            "class": "axis",
            "transform": "translate(" + [margin.left-W_dx(1), 0] + ")",
        }).call(yAxis); // Call the yAxis function on the group

        graph.append("text")
            .attr("class", "legendTitle")
            .attr("x", margin.left-30)
            .attr("y", margin.top-30)
            .text("Pitch");

        //draw_arrow(graph, margin.left-W_dx(2), height-margin.bottom+H_dy(1)/2, margin.left-W_dx(2), margin.top-H_dy(1)/2, "top", "axisLine")

        // Add a title
        graph.append("text")
            .attr("class", "title")
            .attr("x", ((width + margin.left) / 2))
            .attr("y", margin.top / 4)
            .attr("text-anchor", "middle")
            .text(filename);

        graph.append("text")
            .attr("class", "title")
            .attr("x", ((width + margin.left) / 2))
            .attr("y", margin.top/2)
            .attr("text-anchor", "middle")
            .text("Min Z : " + minZ + " Max Z : " + maxZ);

        // Draw the points (x,y,z)
        var pointAttr = {
            x: function(d) {
                return (W(d.x) - W_dx(1)/2);
            },
            y: function(d) {
                return (H(d.y) - H_dy(1)/2);
            },
            width: W_dx(1),
            height: H_dy(1),
            fill: function (d) { return colorScaleRainbow(colorInterpolateRainbow(d.z)); }
        };
        var all_points = graph.selectAll("rect")
            .data(data)
            .enter()
            .append("rect")
            .attr(pointAttr)
            .attr('class', 'pianoroll')
            .on("mouseover", handleMouseOver_rect)
            .on("mouseout", handleMouseOut_rect);

        // // Define event functions
        function handleMouseOver_rect(d, i) {
            // console.log(i);
            d3.select(this)
                .attr("fill", "black")
                .attr("stroke", "red");

            // Specify where to put label of text
            graph.append("text").attr({
                    id: "text" + i, // Create an id for text so we can select it later for removing on mouseout
                    x: function() {
                        return W(d.x) - 10;
                    },
                    y: function() {
                        return H(d.y) - 15;
                    }
                })
                .text(function() {
                    return  "x : " + (d.x) +
                            " y : " + (d.y) +
                            " z : " + (d.z);
                })
                .attr("class", "note_label");
        }

        function handleMouseOut_rect(d, i) {
            // console.log(i);
            d3.select(this)
                .attr({
                    fill: colorScaleRainbow(colorInterpolateRainbow(d.z)),
                    stroke: "none"
                });
            // Select text by id and then remove
            d3.select("#text" + i).remove(); // Remove text location
        }
    });

    function type(d) {
        d.x = +d.x;
        d.y = +d.y;
        d.z = +d.z;
        return d;
    }

    function zoomed() {
      graph.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }

    function draw_arrow(elem, x1, y1, x2, y2, orientation, class_name){
        // Line
        elem.append("line")
            .attr("class", class_name)
            .attr("x1", x1)
            .attr("y1", y1)
            .attr("x2", x2)
            .attr("y2", y2)
    }

</script>
</body>"""

    with open(filename, "wb") as f:
        f.write(text)
    return

if __name__ == '__main__':
    write_numpy_array_html('test.html', 'test')
