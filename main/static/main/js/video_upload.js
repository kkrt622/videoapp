"use strict";

// タイトルフォームの文字数をカウント
function ShowTitleLength(str) {
    document.getElementById('title-form-length').innerHTML = str.length + '/50';
}

// 説明文フォームの文字数をカウント
function ShowDescriptionLength(str) {
    document.getElementById('description-form-length').innerHTML = str.length + '/500';
}

document.addEventListener("DOMContentLoaded", function () {

    // 画像プレビュー
    const thumbnailSample = document.querySelector(".thumbnail-form")
    thumbnailSample.addEventListener("change", function (ev) {
        const image = ev.target.files[0];
        const imageURL = window.URL.createObjectURL(image);
        const sampleImage = document.querySelector(".thumbnail-preview");
        sampleImage.src = imageURL
    })
})

function VideoPreview(obj) {
    const videoForm = document.querySelector(".video-form")
    videoForm.addEventListener("change", function () {
        const reader = new FileReader()
        const videoPreview = document.querySelector(".video-preview")
        reader.addEventListener("load", function () {
            videoPreview.src = reader.result
        })
        reader.readAsDataURL(obj.files[0])
    })
}