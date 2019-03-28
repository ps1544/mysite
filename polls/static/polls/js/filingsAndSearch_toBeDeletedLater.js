// Enable no-conflict mode
/*
PXS: This function in it's current state is at-least getting called. 
That's a start in itself. Now, I need to figure out why is it repeating the 
HTML contents". 

*/
jQuery(document).ready(function () {
    function load_page() {
        // document.write("a10qq32017712017htm");
        //fetch("a10qq32017712017htm" /*, options */)
        //alert("Function called!    ");
        fetch("/polls/static/polls/js/a10qq32017712017htm.html" /*, options */)
            .then((response) => response.text())
            .then((html) => {
                document.getElementById("contents").innerHTML = html;
            })
            .catch((error) => {
                console.warn(error);
            });
    }
});

window.onload = function () {
    load_html();
};

function load_html() {
    // document.write("a10qq32017712017htm");
    //fetch("a10qq32017712017htm" /*, options */)
    //alert("Function called during windows load!");
    document.getElementById("contents").innerHTML='<object type="text/html" data="C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols/AAPL/10-K/a10k20179302017htm.html" ></object>';
    /*
    fetch("polls/static/polls/js/a10qq32017712017htm" )
        .then((response) => response.text())
        .then((html) => {
            document.getElementById("contents").innerHTML = html;
        })
        .catch((error) => {
            console.warn(error);
        });
    */

}

