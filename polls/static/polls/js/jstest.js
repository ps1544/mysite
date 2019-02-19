jQuery(document).ready(function (){
    sortTable(col,dir){
    
    
    $("#pgHeader").html("Daily Returns")
    
    var rows = $('"#mytable" tbody  tr').removeClass('row_alt').get();
    
    var t=1;
    if(!dir || dir=='dec') {
        t=-1;
    } else if(dir=='asc') {
        t=1;
    }
    }
    

    
    rows.sort(function(a, b) {
        var A = $(a).children('td').eq(col).text().toUpperCase();
        var B = $(b).children('td').eq(col).text().toUpperCase();
      
        if(A <b> B) {
          return t;
        }
      
        return 0;
    });
  
    $.each(rows, function(index, row) {
      $('#mytable').children('tbody').append(row);
          if( index%2 == 1){
              $(row).addClass('row_alt');
          }
      
    });
  });