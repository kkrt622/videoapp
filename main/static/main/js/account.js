"use strict";

// 動画表示ボタンの切り替え
var newest = document.querySelector(".account-video-btn-newest");
var popular = document.querySelector(".account-video-btn-popular");
newest.addEventListener("click", function () {
    newest.classList.add("selected")
    popular.classList.remove("selected")
});
popular.addEventListener("click", function () {
    popular.classList.add("selected")
    newest.classList.remove("selected")
});

// プロフィール編集の表示切り替え
var edit_target = document.querySelector('.edit-profile');
var edit_button = document.querySelector('.account-edit-profile-btn');
var edit_close = document.querySelector('.edit-profile-close');
edit_button.addEventListener('click', function () {
    edit_target.classList.toggle('page-visible')
});
edit_close.addEventListener('click', function () {
    edit_target.classList.toggle('page-visible')
});

// 設定の表示切り替え
var settings_target = document.querySelector('.settings');
var settings_button = document.querySelector('.account-settings-btn');
var settings_close = document.querySelector('.settings-close');
settings_button.addEventListener('click', function () {
    settings_target.classList.toggle('page-visible')
});
settings_close.addEventListener('click', function () {
    settings_target.classList.toggle('page-visible')
});

// 画像プレビュー機能の実装
function previewImage(obj) {
    var fileReader = new FileReader();
    fileReader.onload = (function () {
        document.getElementById('preview').src = fileReader.result;
    });
    fileReader.readAsDataURL(obj.files[0]);
}

// 文字数カウント機能
var username = document.getElementById("id_username");
var profile = document.getElementById("id_profile");
var username_count = document.getElementById("edit-username-count");
var profile_count = document.getElementById("edit-profile-count");
// 入力前文字数
username_count.textContent = username.value.length;
profile_count.textContent = profile.value.length;
// 入力時の文字数
username.addEventListener("keyup", function () {
    username_count.textContent = username.value.length;
});
profile.addEventListener("keyup", function () {
    profile_count.textContent = profile.value.length;
});
