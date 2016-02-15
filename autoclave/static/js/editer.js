$(document).ready(function () {
    
    var $calendarElement = $("#my-calendar");
    
    function addEvent(event) {
        eventData.push(event);
        var id = $calendarElement.attr('id') + '_' + event.date;
        var $dowElement = $('#' + id);
        $dowElement.data('hasEvent', true);
        $dowElement.data('values', event.values);
        $dowElement.addClass('event');
    }
    
    $calendarElement.zabuto_calendar({
        data: eventData,
        action: function () {
            return myDateFunction(this.id);
        },
    });
    
    function myDateFunction(id) {
        clear_up_cal_editer();
        myDate = $("#" + id)
        var date = myDate.data("date");
        var hasEvent = myDate.data("hasEvent");
        
        if (hasEvent) {
            editer_image_display(myDate.data("values").path)
            var submit_str = "更改（图片预览还需修正，暂不可靠）";
        } else {
            var submit_str = "生成";
        }
        
        $("#cal-editer-form").html("<form  class=\"form-horizontal\" action=\"/Editer\" method=\"post\"><div class=\"form-group\"><label class=\"col-sm-2 control-label\" for=\"img-text\">文本内容</label><div class=\"col-sm-10\"><input name=\"text\" type=\"text\" class=\"form-control\" id=\"img-text\" placeholder=\"您希望出现在图片中的文字\" " + ( hasEvent ? ("value=\"" + myDate.data('values').text + "\"") : "" ) + " /></div></div><input type=\"hidden\" name=\"date\" value=\"" + date + "\" /><div class=\"form-group\"><div class=\"col-sm-offset-2 col-sm-10\"><a date-has-image=\"" + hasEvent + "\" id=\"cal-editer-submit\" class=\"btn btn-default\">" + submit_str + "</a></div></div><div class=\"form-group\"><div class=\"col-sm-offset-2 col-sm-10\"><p class=\"failure\"></p></div></div></form>");
        
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
    
    function editer_image_display(path) {
        $("#cal-editer-display").html("<img class=\"img-responsive img-thumbnail\" src=\"" + path + "\" alt=\"当日图片\" />");
        $("#cal-editer-display").show();
    }
    
    $("#hide-cal-editer").click(clear_up_cal_editer);
    $("body").on('click', '#cal-editer-submit', function(event){
        form = $("form");
        console.log(build_ajax_data(form.serializeArray()))
        $.ajax({
            method: "POST",
            url: "/Editer",
            data: build_ajax_data(form.serializeArray()),
            error: function(){
                form.find("p.failure").html('<div class="alert alert-danger" role="alert">连接错误，请重试！</div>').show();
            },
            success: function(data){
                if (data.status != 0) {
                    form.find("p.failure").html('<div class="alert alert-danger" role="alert">' + data.dscp + '</div>').show();
                } else {
                    addEvent(data)
                    form.find("p.failure").html('<div class="alert alert-success" role="alert">生成成功！2秒后预览图像</div>').show();
                    window.setTimeout(function(){
                        editer_image_display(data.values.path);
                    },2000);
                }
            }
        });
    });
});