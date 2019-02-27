// Enable no-conflict mode
var $j = jQuery.noConflict();
$j(document).ready(function () {
    
    $j(function (contents) {
        //$("#includedContents").load("C:\Users\pshar\Dropbox\Programming\SampleTexts\FilingsBySymbols\AAPL\10-K\a10k20179302017htm", function());
        $j("#includedContents").load("a10qq32017712017htm");
        alert( "Load was performed." );
    });
});