$(document).ready(function(){
    $.post(
        "/getUnit",
        {},
        function(success){
            $("#unit").html(success);
            getTeacher();
        }
    );    
});

function getTeacher(){
    $.post(
        "/getTeacher",
        {
            'unit': $("#unit").val()
        },function(success){
            $("#teacher").html(success);
        }
    );
}