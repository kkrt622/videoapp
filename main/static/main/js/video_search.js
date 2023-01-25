"use strict";

const url = new URL(window.location.href);
const params = url.searchParams;

document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector(".search-form")
    searchForm.addEventListener("keydown", function (ev) {
        if (ev.key == "Enter") {
            var keyword = searchForm.value;
            const xhr = new XMLHttpRequest();
            const url = window.location.href.replace(/\?.*$/, "");
            const queryString = new URLSearchParams({ "keyword": keyword }).toString();
            const requestPath = url + "?" + queryString;
            xhr.open("GET", requestPath);
            xhr.responseType = "document";
            xhr.send();
            xhr.onreadystatechange = () => {
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {
                        const res = xhr.response;
                        const videoList = document.querySelector(".video-list-container")
                        const newDom = res.querySelectorAll(".video-information-container");
                        const oldDom = document.querySelectorAll(".video-information-container")
                        if (newDom) {
                            oldDom.forEach((element) => {
                                videoList.removeChild(element);
                            });
                            newDom.forEach((element) => {
                                videoList.appendChild(element);
                            });
                        }
                    }
                    else {
                        window.alert("通信に失敗しました。");
                    }
                }
            }
        }
    })


    const searchButtonList = document.querySelectorAll(".search-button");
    searchButtonList.forEach(function (element, index) {
        element.addEventListener("click", function (ev) {
            // ボタンデザインの切り替え
            var preActiveButton = document.querySelector(".active")
            preActiveButton.classList.remove("active")
            element.classList.add("active")
            // 「人気の動画」を選択すると閲覧回数が多い順に表示する
            const xhr = new XMLHttpRequest();
            const url = window.location.href.replace(/\?.*$/, "");
            if (element == searchButtonList[1]) {
                const queryString = new URLSearchParams({ "btnType": "favorite" }).toString();
                const requestPath = url + "?" + queryString;
                xhr.open("GET", requestPath);
                xhr.responseType = "document";
                xhr.send();
                xhr.onreadystatechange = () => {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            const res = xhr.response;
                            const videoList = document.querySelector(".video-list-container")
                            const newDom = res.querySelectorAll(".video-information-container");
                            const oldDom = document.querySelectorAll(".video-information-container")
                            if (newDom) {
                                oldDom.forEach((element) => {
                                    videoList.removeChild(element);
                                });
                                newDom.forEach((element) => {
                                    videoList.appendChild(element);
                                });
                            }
                        }
                        else {
                            window.alert("通信に失敗しました。");
                        }
                    }
                }
            }
            else {
                const queryString = new URLSearchParams({ "btnType": "all" }).toString();
                const requestPath = url + "?" + queryString;
                xhr.open("GET", requestPath);
                xhr.responseType = "document";
                xhr.send();
                xhr.onreadystatechange = () => {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            const res = xhr.response;
                            const videoList = document.querySelector(".video-list-container")
                            const newDom = res.querySelectorAll(".video-information-container");
                            const oldDom = document.querySelectorAll(".video-information-container")
                            if (newDom) {
                                oldDom.forEach((element) => {
                                    videoList.removeChild(element);
                                });
                                newDom.forEach((element) => {
                                    videoList.appendChild(element);
                                });
                            }
                        }
                        else {
                            window.alert("通信に失敗しました。");
                        }
                    }
                }
            }
        })
    })
})