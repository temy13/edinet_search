// ▼①元のHTMLソースを保持しておく変数
var backupOriginal = "";
// ▼②文字列を検索してハイライト用要素を加える処理
function replacer( str, word , att  ) {
    var SearchString = '(' + word + ')';
    var RegularExp = new RegExp( SearchString, "g" );
    var ReplaceString = '<span class="' + att + '">$1</span>';
    var ResString = str.replace( RegularExp , ReplaceString );
    return ResString;
}
// ▼③ハイライトを加える処理
function addhighlight() {
    backupOriginal = $(".content").html();
    var forShow = backupOriginal;
    q = $("#query").val()
    forShow = replacer( forShow, q, "mark1" );
    // forShow = replacer( forShow, , "mark2" );
    // forShow = replacer( forShow, "表示", "mark3" );
    $(".content").html(forShow);
}
// ▼④ハイライトを消す処理
function clearhighlight() {
    $(".content").html(backupOriginal);  // バックアップから書き戻す
    backupOriginal = "";    // バックアップを消す
}
// ▼⑤ハイライトを加えるか消すかを判断
function highlightcheck() {
    if( backupOriginal.length == 0 ) {
        // 何もバックアップされていなければ（未ハイライトなので）ハイライトを加える
        addhighlight();
    }
    else {
        // 何かバックアップされていれば（ハイライト済みなので）ハイライトを消す
        clearhighlight();
    }
}
$(document).ready(function(){
  highlightcheck()
});
