
var gratia_regex = /\/gratia\/.*?\//
var static_gratia_regex = /\/gratia\/(today)|(static)/
    
function replace_url_to_analize(url_param){
    return url_param.replace(gratia_regex,'/gratia/html/')
}
function replace_url_to_csv(url_param){
    return url_param.replace(gratia_regex,'/gratia/csv/')
}

function endsWith(str, suffix) {
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function resizeIframe(ifrm) {
  setTimeout(function(){
    ifrm.style.width = ifrm.contentWindow.document.body.scrollWidth + 'px';
    var total_height = 0
    total_height += $('#gc_title_div', ifrm.contentWindow.document).height();
    console.log(total_height);
    total_height += $('#gc_chart_div', ifrm.contentWindow.document).height();
    console.log(total_height);
    total_height += $('#gc_legend_div', ifrm.contentWindow.document).height();
    console.log(total_height);
    ifrm.style.height=total_height + "px";
  },1000);
}

$('iframe').each(function(index,e){
    if(e.src && e.src.match(gratia_regex) && !e.src.match(static_gratia_regex)){
        resizeIframe(e);
        var new_url = e.src.replace("&no_html_frame=y","");
        var str ='<br/>(<a href="'+replace_url_to_analize(new_url)+'">Analyze</a>)(<a href="'+replace_url_to_csv(new_url)+'">View raw data</a>)<hr/>';
        $(e).after(str);
    }
})