$(document).ready(function () {
  var layout_select = $("select[name=layout]")
  var form = $("form")

  if (!email_confirmed) {
    $("select").prop( "disabled", true );
    $("input[type!=hidden]").prop( "disabled", true );
    if (typeof alert_bar === 'undefined') {
      form.find("p.failure").html('<div class="alert alert-warning" role="alert">您需要确认邮箱，才可更改设置。</div>');
      form.find("div.failure").show();
    }
  }
  if (typeof alert_bar !== 'undefined') {
    form.find("p.failure").html(alert_bar)
    form.find("div.failure").show()
  }

  layout_select.change(function() {
    var layout_id = layout_select.find("option:selected").data('display');
    $("#layout-display").html('<img class="thumbnail img-responsive" src="' + layout_id + '" />').show()
  });
  $("#release-pair").click(function() {
    $.ajax({
        method: "DELETE",
        url: "/Setting/Pair",
        data: build_ajax_data([]),
        error: function(){
            form.find("p.failure").html('<div class="alert alert-danger" role="alert">连接错误，请重试！</div>');
            form.find("div.failure").show();
        },
        success: function(data){
            if (data.status != 0) {
                form.find("p.failure").html('<div class="alert alert-danger" role="alert">' + data.dscp + '</div>');
                form.find("div.failure").show();
            } else {
                form.find("p.failure").html('<div class="alert alert-success" role="alert">完成释放，2秒后刷新。</div>');
                form.find("div.failure").show();
                window.setTimeout(function(){
                    location.reload(true);
                },2000);
            }
        }
    });
  });
});