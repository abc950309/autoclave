$(document).ready(function () {
  var layout_select = $("select[name=layout]")
  layout_select.change(function() {
    var layout_id = layout_select.find("option:selected").data('display');
    $("#layout-display").html('<img class="thumbnail img-responsive" src="' + layout_id + '" />').show()
  });
});