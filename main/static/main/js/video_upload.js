// タイトルフォームの文字数をカウント
function ShowTitleLength(str) {
    document.getElementById('title-form-length').innerHTML = str.length + '/50';
}

// 説明文フォームの文字数をカウント
function ShowDescriptionLength(str) {
    document.getElementById('description-form-length').innerHTML = str.length + '/500';
}

document.addEventListener("DOMContentLoaded", function () {
    var thumbnailSample = document.querySelector(".thumbnail-form")
    thumbnailSample.addEventListener("change", function (ev) {
        var image = ev.target.files[0];
        var imageURL = window.URL.createObjectURL(image);
        var sampleImage = document.querySelector(".thumbnail-preview");
        sampleImage.src = imageURL
    })
})