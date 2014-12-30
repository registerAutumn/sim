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
                var p = $("<p>");
                var title = $("<h3>").text(t.courseName + "－" + teacher);
                var comment = $("<input>").attr('type', 'text')
                                          .attr('id', 'comment')
                                          .addClass('form-control-static')
                                          .addClass('col-lg-8');
                var submits = $("<input>").attr('type', 'button')
                                          .addClass('btn')
                                          .addClass('btn-primary')
                                          .attr('value', '留下評論')
                                          .click(function(){
                                            title = $(this).prev().prev().text().replace("－", ",")
                                            data = $(this).prev().val();
                                            $.post(
                                                "/addComment",
                                                {
                                                    courseName: title,
                                                    data: data
                                                },
                                                function(){
                                                    search();
                                                }
                                            );
                                          });
                title.appendTo(p);
                comment.appendTo(p);
                submits.appendTo(p);
                p.appendTo(block);
                for (var i = 0; i < t.comment.length; i++) {
                    var li = $("<li>").text(t.comment[i]);
                    li.appendTo(block);
                    //console.log(li);
                }
                block.appendTo($(".lower"));
            }
        },
        "JSON"
    )
}