"use strict";

// 文字数カウント機能
const title = document.getElementById("id_title");
const description = document.getElementById("id_description");
const title_count = document.getElementById("title-form-count");
const description_count = document.getElementById("description-form-count");

// 入力前文字数
title_count.textContent = title.value.length;
description_count.textContent = description.value.length;
// 入力時の文字数
title.addEventListener("keyup", function () {
    title_count.textContent = title.value.length;
});
description.addEventListener("keyup", function () {
    description_count.textContent = description.value.length;
});

document.addEventListener("DOMContentLoaded", function () {
    const thumbnailSample = document.querySelector(".thumbnail-form")
    thumbnailSample.addEventListener("change", function (ev) {
        const image = ev.target.files[0];
        const imageURL = window.URL.createObjectURL(image);
        const sampleImage = document.querySelector(".thumbnail-preview");
        sampleImage.src = imageURL
    })
})

// ポップアップウィンドウの表示
const deleteFormWindow = document.querySelector(".delete-form-container")
const updateFormWindow = document.querySelector(".update-form-container")
const overlay = document.querySelector(".overlay")
const cancelBtn = document.querySelector(".cancel-btn")
const openBtn = document.querySelector(".delete-btn")

openBtn.addEventListener("click", function () {
    deleteFormWindow.classList.toggle("closed")
    updateFormWindow.classList.toggle("closed")
    overlay.classList.toggle("closed")
})

cancelBtn.addEventListener("click", function () {
    deleteFormWindow.classList.toggle("closed")
    updateFormWindow.classList.toggle("closed")
    overlay.classList.toggle("closed")
})
