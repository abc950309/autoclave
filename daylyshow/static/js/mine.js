function getCookie(name) {
    var c = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return c ? c[1] : undefined;
}

function build_ajax_data(data){
    data.push({ name: "ajax_flag", value: true });
    for(var i = 0, l = data.length; i < l; i++) {
        if (data[i]['name'] == "_xsrf"){
            return data
        }
    }
    data.push({ name: "_xsrf", value: getCookie("_xsrf") });
    return data
}
