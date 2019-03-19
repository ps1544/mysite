// Enable no-conflict mode
/*
PXS: This function in it's current state is at-least getting called. 
That's a start in itself. Now, I need to figure out why is it repeating the 
HTML contents". 

*/
jQuery(document).ready(function () {
    function load_home(e) {
        // document.write("a10qq32017712017htm");
        //fetch("a10qq32017712017htm" /*, options */)
        fetch("/polls/dailyReturns/" /*, options */)
            .then((response) => response.text())
            .then((html) => {
                document.getElementById("contents").innerHTML = html;
            })
            .catch((error) => {
                console.warn(error);
            });
    }
});
