//  sortTable(f,n)
//  f : 1 ascending order, -1 descending order
//  n : n-th child(<td>) of <tr>

jQuery(document).ready(function(){
//jQuery("#pgHeader").html("Top 100 Stocks by Transaction Volume");

/*
var item = $("#rowData").text();
if (item == "date"){
}

var elem = $("#date");  
elem.css('visibility', 'hidden'); 
var elem = $("#rowData");  
elem.css('visibility', 'hidden'); 

*/


function sortTable(f,n){
    
    var rows = $('#mytable tbody  tr').get();

    rows.sort(function(a, b) {

        var A = getVal(a);
        var B = getVal(b);

        if(A < B) {
            return -1*f;
        }
        if(A > B) {
            return 1*f;
        }
        return 0;
    });

    function getVal(elm){
        var v = $(elm).children('td').eq(n).text().toUpperCase();
        if($.isNumeric(v)){
            v = parseInt(v,10);
        }
        return v;
    }

    $.each(rows, function(index, row) {
        $('#mytable').children('tbody').append(row);
    });
}

var f_sl = 1; // flag to toggle the sorting order
var f_nm = 1; // flag to toggle the sorting order

$("#company").click(function(){
    f_sl *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_sl,n);
});

$("#symbol").click(function(){
    f_sl *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_sl,n);
});

$("#open").click(function(){
    f_sl *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_sl,n);
});

$("#high").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
});

$("#low").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#close").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#netchg").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#pcntchg").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})


$("#vol").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#52wkhigh").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})


$("#52wklow").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})


$("#pe").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#ytd").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#date").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

$("#DlrVolume").click(function(){
    f_nm *= -1; // toggle the sorting order
    var n = $(this).prevAll().length;
    sortTable(f_nm,n);
})

});