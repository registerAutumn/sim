var cols = "零一二三四五六日";
function search(){
    options = $("input[name=option]");
    for (var i = 0; i < options.length; i++) {
        if($(options[i]).hasClass('btn-success')){break;}
    };
    $("#show>li").remove();
    $.post(
        "/SearchResult",
        {
            key: $("#keys").val(),
            unit: $("#unit").val(),
            type: i
        },
        function(success){
            data = eval(success).data;
            if(data.length == 0){
                var li = $("<li>").text("沒有\"" + $("#keys").val() +"\"的課程");
                li.appendTo($("#show"));
            }
            for (var i = 0; i < data.length; i++) {
                d = data[i];
                var li = $("<li>")
                         .attr("teacher", d.courseTeacher)
                         .attr("time", d.courseTime)
                         .attr("message", "上課時間：" + d.Time + "<br>上課地點：" + d.courseRoom + "<br>上課班級：" + d.className + "<br>開課老師：" + d.courseTeacher)
                         .click(function(){
                            var temp = $(this).attr('time').split(",");
                            search_action($(this), 'fill')
                            var clone = $(this).clone();
                            clone.click(function(){
                                var check = confirm('確定要刪除?');
                                if(check){
                                    search_action($(this), 'remove');
                                    $(this).remove();
                                }
                                search();
                            }).mouseover(function(){
                                $(".explain").eq(0).html($(this).attr('message'));
                                $(".explain").eq(0).css("display", "block");
                            });
                            clone.appendTo("#remove");
                            $(this).remove();
                            var li = $("#show>li");
                            for(var i = 0; i < li.length; i++){
                                result = search_action($(li[i]), 'check');
                                if(!result){
                                    $(li[i]).remove();
                                }
                            }
                         })
                         .mouseover(function(){
                            $(".explain").eq(0).html($(this).attr('message'));
                            $(".explain").eq(0).css("display", "block");
                            search_action($(this), 'fill')
                         }).mouseout(function(){
                            search_action($(this), 'remove')
                         }).text(d.courseName);
                if(!search_action($(li), 'check')){
                    $(li).attr("message", "衝堂").click(undefined);
                    continue;
                }
                if(search_action($(li), 'is_exists')){
                    $("#show").append(li);                            
                }
            };
        },
        "JSON"
    );
}

function load_course(){
    $.get(
        "/getCourse",
        function(success){
            var grid = eval(success);
            html = "<tr><td width='200' align='center'>時間</td><td width='200' align='center'>一</td><td width='200' align='center'>二</td><td width='200' align='center'>三</td><td width='200' align='center'>四</td><td width='200' align='center'>五</td><td width='200' align='center'>六</td><td width='200' align='center'>日</td></tr>"
            for (var i = 0; i < grid.length; i++) {
                html += "<tr>"
                for (var j = 0; j < grid[i].length; j++) {
                    if(grid[i][j] == "<td width='200' align='center' tags='A'>A</td>" || grid[i][j] == "<td width='200' align='center' tags='B'>B</td>"){
                        html = html.substring(0, html.length - 4);
                        break;
                    }
                    html += grid[i][j];
                }
                html += "</tr>"
                if(grid[i][j] == "<td width='200' align='center' tags='A'>A</td>" || grid[i][j] == "<td width='200' align='center' tags='B'>B</td>"){
                    html = html.substring(0, html.length - 4);
                }
            }
            $(".responstable").html(html);
            restore();
            var td = $("td");
            for(var i = 0 ; i < td.length; i++){
                $(td[i]).mouseover(function(){
                    if($(this).attr("tags").length != 0){
                        $("#showTime").html($(this).attr("tags"));
                        $("#showTime").css("display", "block");
                    }
                }).mouseout(function(){
                    $("#showTime").css("display", "none");
                });
            }
        },
        "JSON"
    ).fail(function(){
        $(".lightbox").fadeIn('500');
        $(".frame").fadeIn('500');        
    });
}

function search_action(resource, action){

    var temp = resource.attr('time').replace('M', 0);
    while(temp.indexOf("M") != -1){
        temp = temp.replace('M', 0);
    }
    temp = temp.split(",");
    for (var i = 1; i < temp.length; i+=2) {
        if(cols.indexOf(temp[i])!=-1){
            var col = cols.indexOf(temp[i]);
            if(temp[i+1].indexOf("-")!=-1){
                var row = temp[i+1].split("-");
                var start = parseInt(row[0])+1;
                var end = parseInt(row[1])+1;
            }else{
                var start = parseInt(temp[i+1])+1;
                var end = parseInt(temp[i+1])+1;
            }
        }else{
            var col = cols.indexOf(temp[i-2]);
            if(temp[i].indexOf("-")!=-1){
                var row = temp[i].split("-");
                var start = parseInt(row[0])+1;
                var end = parseInt(row[1])+1;
            }else{
                var start = parseInt(temp[i+1])+1;
                var end = parseInt(temp[i+1])+1;
            }
        }
        var tr = $("tr")
        for(var j = start; j <= end; j++){
            var td = $(tr[j]).children('td');
            switch(action){
                case 'check':
                    if($(td[col]).text().charCodeAt(0) != 160 && $(td[col]).text().length != 0){
                        return false;
                    }
                    break;
                case 'fill':
                    $(td[col]).text(resource.text());
                    break;
                case 'remove':
                    $(td[col]).text(String.fromCharCode(160));
                    break;
                case 'is_exists':
                    if ($(td[col]).text() == resource.text().split("--")[0]){
                        return false;
                    }
                    break;
            }
        }
    };
    return true;
}

function save(){
    var selected = $("#remove > li");
    var li_html = ""
    for(var i = 0 ; i < selected.length; i++){
        li_html += selected[i].outerHTML;
    }
    $.post(
        "/store",
        {
            data: li_html
        },
        function(success){
            var msg = eval(success);
        },
        "JSON"
    );
}

function restore(){
    $("#remove>li").remove();
    $.post(
        "/restore",
        {},
        function(success){
            var temp = eval(success);
            if(temp.success){
                var data = $(temp.table);
                for(var i = 0; i < data.length; i++){
                    search_action($(data[i]), 'fill');
                    $(data[i]).click(function(){
                        var check = confirm('確定要刪除?');
                        if(check){
                            search_action($(this), 'remove');
                            $(this).remove();
                        }
                    }).mouseover(function(){
                                $(".explain").eq(0).html($(this).attr('message'));
                                $(".explain").eq(0).css("display", "block");
                    }).appendTo($("#remove"));

                }
            }
        },
        "JSON"
    );
}
function load_unit(){
    $.post(
        "/getUnit",
        {},
        function(success){
            $("#unit").html($("unit").html() + success);
        }
    );
}

function checked(){
    $(".frame").fadeOut('1000');
    $.post(
        '/check_login',
        {
            username: $("#Users").val(),
            password: $("#Password").val()
        },
        function(success){
            message = eval(success);
            if(message.success){
                $(".lightbox").fadeOut('500');
                load_course();
            }else{
                alert(message.message);
                $(".frame").fadeIn('1000');
            }
        },"json");
}

function exports(){
        html2canvas($("table").eq(0),{
            onrendered:function(canvas){
                document.body.appendChild(canvas)
                var data = document.getElementsByTagName('canvas')[0];
                var a = document.createElement("a");
                a.href = data.toDataURL();
                a.download = "Course.jpg";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                $("canvas").remove();
            }
        })
}

function toggle(clicks){
    $("input[name=option]").removeClass('btn-success');
    $(clicks).addClass('btn-success')
}