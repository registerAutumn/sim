$(document).ready(function(){
    $.post(
        "/getUnit",
        {},
        function(success){
            $("#unit").html($("unit").html() + success);
        }
    );    
});

function search(){
    $(".lower").children("div").remove();
    $.post(
        "/getTeacherList",
        {
            keys: $("#keys").val(),
            unit: $("#unit").val()
        },
        function(success){
            var temp = eval(success).data;
            for(var teacher in temp){
                var t = temp[teacher]
                var block = $("<div>").addClass('block');
                var title = $("<h3>").text(t.courseName + "－" + teacher);
                title.appendTo(block);
                block.appendTo($(".lower"));
            }
        },
        "JSON"
    )
}