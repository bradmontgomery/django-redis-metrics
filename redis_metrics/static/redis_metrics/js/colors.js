/*
 * This is bascially a lookup table for colors used with Chart.js
 *
 * usage:
 *
 *  Color(0).fillColor
 *  Color(0).highlightFill
 *  Color(0).strokeColor
 *  Color(0).highlightStroke
 *
 */

var Color = function(index) {
    // Basic Colors
    var colors = [
        "255,102,102", // Red
        "255,178,102", // Orange
        "255,255,102", // Yellow
        "102,255,102", // Green
        "102,255,255", // Turquoise
        "102,102,255", // Blue
        "178,102,255", // Purple
        "255,102,178", // Pink
    ];
    // Highlight Colors
    var hl_colors = [
        "255,0,0",   // Red
        "255,128,0", // Orange,
        "255,255,0", // Yellow
        "0,255,0",   // Green
        "0,255,255", // Turquoise
        "0,0,255",   // Blue
        "127,0,255", // Purple
        "255,0,127", // Pink
    ];

    return {
        fillColor: "rgba(" + colors[index % 8] + ",0.5)",
        strokeColor: "rgba(220,220,220,0.8)",
        highlightFill: "rgba(" + hl_colors[index % 8] + ",0.75)",
        highlightStroke: "rgba(220,220,220,1)",
    };
};
