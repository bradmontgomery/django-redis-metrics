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

var DefaultColor = function(index) {
    // Basic Colors
    var colors = [
        "255,102,102", // Red
        "255,178,102", // Orange
        "102,255,102", // Green
        "102,102,255", // Blue
        "102,255,255", // Turquoise
        "178,102,255", // Purple
        "255,102,178", // Pink
        "204,204,0",   // Yellow
    ];
    // Highlight Colors
    var hl_colors = [
        "255,0,0",   // Red
        "255,128,0", // Orange,
        "0,255,0",   // Green
        "0,0,255",   // Blue
        "0,255,255", // Turquoise
        "127,0,255", // Purple
        "255,0,127", // Pink
        "255,255,0", // Yellow
    ];

    return {
        fillColor: "rgba(" + colors[index % colors.length] + ",0.5)",
        strokeColor: "rgba(220,220,220,0.8)",
        highlightFill: "rgba(" + hl_colors[index % colors.length] + ",0.75)",
        highlightStroke: "rgba(220,220,220,1)",
    };
};
