// Enable no-conflict mode
/*
PXS: This function in it's current state is at-least getting called. 
That's a start in itself. Now, I need to figure out why is it repeating the 
HTML contents". 

*/
$( document ).ready(function() {
    $( "#includedContent" ).load( "filename.html", function() {
    //$( "#includedContent" ).load( "/C:/Users/pshar/Dropbox/WebServices/mysite/polls/templates/polls/filename.html", function() {
        alert( "Loaded local web page." );
    })
});
    