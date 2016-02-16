$( document ).ready(function() {
    $(".login-switchs").click(function() {
        $(this).parentsUntil("div#login-form-base").removeClass("selected");
        if ( $(this).hasClass("return-switch") ) {
            $(".view-switches").addClass("selected");
        } else if ( $(this).hasClass("login-switch") ) {
            $(".view-login").addClass("selected");
        } else if ( $(this).hasClass("register-switch") ) {
            $(".view-register").addClass("selected");
        } else if ( $(this).hasClass("unable-login-switch") ) {
            $(".view-register").addClass("selected");
        }
    });
    
    $("form").submit(function(){
        var form = $(this);
        var button = form.find("button[type=submit]");
        button.attr('disabled',true);
        var old_button_text = button.html();
        if ( form.hasClass("register") ) {
            button.html('<i class="fa fa-spinner fa-spin"></i> 注册中');
            next = "/Setting/Email"
        } else if ( form.hasClass("login") ) {
            button.html('<i class="fa fa-spinner fa-spin"></i> 登陆中');
        }
        
        var post_data = build_ajax_data(form.serializeArray());
        console.log(post_data);
        $.ajax({
            url: form.attr('action'),
            type: "post",
            data: post_data,
            timeout: 10000,
            error: function(){
                button.html(old_button_text).attr('disabled', false);
                form.find("p.failure").html('<div class="alert alert-danger" role="alert">连接错误，请重试！</div>').show();
            },
            success: function(data){
                if (data.status != 0) {
                    button.html(old_button_text).attr('disabled', false);
                    form.find("p.failure").html('<div class="alert alert-danger" role="alert">' + data.dscp + '</div>').show();
                } else {
                    button.html('<i class="fa fa-spinner fa-spin"></i> 正在跳转').attr('disabled', false);
                    form.find("p.failure").html('<div class="alert alert-success" role="alert">' + data.dscp + '</div>').show();
                    window.setTimeout(function(){location.href=next},2000);
                }
            }
        });
        return false;
    });
});