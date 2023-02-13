"use strict";

// プロフィール編集の表示切り替え
const edit_target = document.querySelector('.edit-profile');
const edit_button = document.querySelector('.account-edit-profile-btn');
const edit_close = document.querySelector('.edit-profile-close');
edit_button.addEventListener('click', function () {
    edit_target.classList.toggle('page-visible')
});
edit_close.addEventListener('click', function () {
    edit_target.classList.toggle('page-visible')
});

// 設定の表示切り替え
const settings_target = document.querySelector('.settings');
const settings_button = document.querySelector('.account-settings-btn');
const settings_close = document.querySelector('.settings-close');
settings_button.addEventListener('click', function () {
    settings_target.classList.toggle('page-visible')
});
settings_close.addEventListener('click', function () {
    settings_target.classList.toggle('page-visible')
});

// 画像プレビュー機能の実装
function previewImage(obj) {
    const fileReader = new FileReader();
    fileReader.onload = (function () {
        document.getElementById('preview').src = fileReader.result;
    });
    fileReader.readAsDataURL(obj.files[0]);
}

// 文字数カウント機能
const username = document.getElementById("id_username");
const profile = document.getElementById("id_profile");
const username_count = document.getElementById("edit-username-count");
const profile_count = document.getElementById("edit-profile-count");
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
