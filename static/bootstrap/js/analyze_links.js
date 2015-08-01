
var gratia_regex = /\/gratia\/.*?\//
var static_gratia_regex = /\/gratia\/(today)|(static)/
    
function replace_url_to_analize(url_param){
    return url_param.replace(gratia_regex,'/gratia/xml/')
}
function replace_url_to_csv(url_param){
    return url_param.replace(gratia_regex,'/gratia/csv/')
}

function endsWith(str, suffix) {
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

$('img').each(function(index,e){
    if(e.src && e.src.match(gratia_regex) && !e.src.match(static_gratia_regex)){
        var str ='<br/>(<a href="'+replace_url_to_analize(e.src)+'">Analyze</a>)(<a href="'+replace_url_to_csv(e.src)+'">View raw data</a>)<hr/>'
        $(e).after(str)
    }
})