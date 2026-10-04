/* Likes, comments and follow buttons: small fetch() calls, no dependencies. */
(function () {
    "use strict";

    const csrfToken = document.body.dataset.csrf;

    async function post(url, body) {
        const response = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest" },
            body: body,
        });
        if (response.status === 401 || response.redirected) {
            window.location.href = "/accounts/login/";
            throw new Error("not authenticated");
        }
        if (!response.ok) {
            throw new Error("Request failed: " + response.status);
        }
        return response.json();
    }

    document.addEventListener("click", async (event) => {
        const likeBtn = event.target.closest(".js-like");
        if (likeBtn) {
            const data = await post(likeBtn.dataset.url);
            const postId = likeBtn.dataset.post;
            document.querySelectorAll('.js-like[data-post="' + postId + '"]').forEach((btn) => {
                btn.querySelector("i").classList.toggle("liked", data.liked);
                btn.setAttribute("aria-pressed", data.liked);
            });
            document.querySelectorAll('[data-like-count="' + postId + '"]').forEach((el) => {
                el.textContent = data.count;
            });
            return;
        }

        const followBtn = event.target.closest(".js-follow");
        if (followBtn) {
            const data = await post(followBtn.dataset.url);
            followBtn.textContent = data.following ? "Segui già" : "Segui";
            followBtn.classList.toggle("btn-light", data.following);
            followBtn.classList.toggle("btn-primary", !data.following);
            const counter = document.querySelector("[data-follower-count]");
            if (counter) counter.textContent = data.followers;
        }
    });

    document.addEventListener("submit", async (event) => {
        const form = event.target.closest(".js-comment-form");
        if (!form) return;
        event.preventDefault();
        const input = form.elements.text;
        if (!input.value.trim()) return;
        const data = await post(form.dataset.url, new FormData(form));
        document.querySelectorAll('[data-comments="' + form.dataset.post + '"]').forEach((list) => {
            const placeholder = list.querySelector(".js-no-comments");
            if (placeholder) placeholder.remove();
            list.insertAdjacentHTML("afterbegin", data.html);
        });
        input.value = "";
    });
})();
