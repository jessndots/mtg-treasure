$(function(){})


$('.card-table').on('click', $('.edit'), function(evt) {
    $tr = $(evt.target).parent().parent()
    console.log($tr)
    // create drop down for set
    $setTd = $tr.children()[7]
    console.log($setTd)
    
    

    // create button to change to/from foil 

    // add button to increase/decrease count

    // add button to split

})
