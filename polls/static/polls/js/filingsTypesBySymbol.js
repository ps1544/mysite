jQuery(document).ready(function(){


    $( "filingType" ).on( "click", function() {
        var hrefLink = document.getElementById("filingType").getAttribute("href");
        //url = hrefLink.replace(/\\/g,"/");
        location.href = hrefLink
        // Alternatively, to open in a new window use: window.location = url;
        //window.location = url
        
        
    })
    

})