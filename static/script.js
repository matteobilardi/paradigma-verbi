var offset = 0;

var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
};

function escapeHtml(string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s];
  });
}


/*
function highlightYellow(position) {
    var htmlText = $("#text").html();
    var start = position[0] + offset;
    var end = position[1] + offset;
    var highlightedWord = "<mark>" + htmlText.slice(start, end) + "</mark>";
    console.log("word = " + highlightedWord + " offset = " + offset);
    htmlText = htmlText.slice(0, start) + highlightedWord + htmlText.slice(end);
    offset += "<mark></mark>".length;
    $("#text").html(htmlText);
}
*/


function highlight(position, paradigmsToPrint) {
    var htmlText = $("#text").html();
    var start = position[0] + offset;
    var end = position[1] + offset;
    var highlightedWord = "<a href=\"#\" data-toggle=\"tooltip\" title=\"" + paradigmsToPrint + "\">" + htmlText.slice(start, end) + "</a>";
    //console.log("word = " + highlightedWord + " offset = " + offset);
    htmlText = htmlText.slice(0, start) + highlightedWord + htmlText.slice(end);
    offset += ("<a href=\"#\" data-toggle=\"tooltip\" title=\"" + paradigmsToPrint + "\"></a>").length;
    $("#text").html(htmlText);
    //$('[data-toggle="tooltip"]').tooltip(); // Not working when uncommented because its insertion into html are not taken into account by offset
}


$(document).ready(function() {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/analyze');

    socket.on("verb_from_server", function(data) {
        //console.log(data);
        var htmlToPrint = "<p><b>" + data.verb.word + "</b>: ";
        //console.log("paradigms: " + data.verb.paradigms);
        var paradigmsToPrint = "";
        for (var i = 0; i < data.verb.paradigms.length; i++) {
            if (i > 0 && i < data.verb.paradigms.length) {
                paradigmsToPrint += " | ";
            }
            paradigmsToPrint += data.verb.paradigms[i];
        }
        highlight(data.verb.position, paradigmsToPrint);
        htmlToPrint += paradigmsToPrint + "</p>";
        $("#paradigms").append(htmlToPrint);

    });

/*    socket.on("verbs_from_server", function(data) {
        var htmlToPrint = "";
        console.log(data);
        for(var i = 0; i < data.length; i++) {
            var verb = data[i].verb;
            //console.log(data);
            var verbHtmlToPrint = "<p><b>" + verb.word + "</b>: ";
            //console.log("paradigms: " + data.verb.paradigms);
            var paradigmsToPrint = "";
            for (var j = 0; j < verb.paradigms.length; j++) {
                if (j > 0 && j < verb.paradigms.length) {
                    paradigmsToPrint += " | ";
                }
                paradigmsToPrint += verb.paradigms;
            }
            highlight(verb.position, paradigmsToPrint);
            verbHtmlToPrint += paradigmsToPrint + "</p>";
            htmlToPrint += verbHtmlToPrint;
        }
        $("#paradigms").append(htmlToPrint);
    });*/

    $("#submit_text").click(function(event) {
        nonStyledText = escapeHtml($("#text")[0].innerText); //Not using JQuery's .text() as it doesn't preserve newlines
        $("#text").html(nonStyledText);
        $("#paradigms").html(""); // Clean Results
        offset = 0; // Reset offset
        socket.emit("text_from_client", {"text": $("#text").html(), "lang": $("#lang").val()});
        event.preventDefault();
    });
});
