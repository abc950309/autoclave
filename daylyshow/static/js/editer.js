$(document).ready(function () {
    $("#my-calendar").zabuto_calendar({
        data: eventData,
        action: function () {
            return myDateFunction(this.id);
        },
    });
    
    function myDateFunction(id) {
        clear_up_cal_editer();
        var date = $("#" + id).data("date");
        var hasEvent = $("#" + id).data("hasEvent");
        
        if (hasEvent) {
            $("#cal-editer-display").html("<img class=\"img-responsive img-thumbnail\" src=\"/static/output/" + to_says + date + ".png\" alt=\"当日图片\" />");
            $("#cal-editer-display").show();
            var submit_str = "更改（图片预览还需修正，暂不可靠）";
        } else {
            var submit_str = "生成";
        }
        
        
        $("#cal-editer-form").html("<form action=\"/{{ name }}/edit\" method=\"post\"><div class=\"form-group\"><label for=\"img-text\">文本内容</label><input name=\"text\" type=\"text\" class=\"form-control\" id=\"img-text\" placeholder=\"您希望出现在图片中的文字\"></div><input type=\"hidden\" name=\"date\" value=\"" + date + "\" /><a date-has-image=\"" + hasEvent + "\" id=\"cal-editer-submit\" class=\"btn btn-default\">" + submit_str + "</button></form>");
        
        $("#cal-editer-date").html(date);
        $("#cal-editer").show();
        
        return true;
    }
    function clear_up_cal_editer() {
        $("#cal-editer").hide();
        $("#cal-editer-display").hide();
        $("#cal-editer-display").html("");
        $("#cal-editer-form").html("");
        return true;
    }
    $("#hide-cal-editer").click(clear_up_cal_editer);
    
    $("body").on('click', '#cal-editer-submit', function(event){
        $.ajax({
            method: "POST",
            url: "/{{ name }}/edit",
            data: $("form").serialize()
        });
        $("#cal-editer-display").html("<img class=\"img-responsive img-thumbnail\" src=\"/static/output/" + to_says + $("input[name=date]").val() + ".png\" alt=\"当日图片\" />");
        $("#cal-editer-display").show();
        eventData.push({"date": $("input[name=date]").val()});
    });
});