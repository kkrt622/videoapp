// タイトルフォームの文字数をカウント
function ShowTitleLength(str) {
    document.getElementById('title-form-length').innerHTML = str.length + '/50';
}

// 説明文フォームの文字数をカウント
function ShowDescriptionLength(str) {
    document.getElementById('description-form-length').innerHTML = str.length + '/500';
}