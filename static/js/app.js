$(document).ready(function () {
    const BASE_URL = window.location.pathname.endsWith('/')
        ? window.location.pathname
        : window.location.pathname + '/';

    let token = localStorage.getItem("token");

    // Show/hide login form based on token presence
    if (token !== null) {
        $("#login-form-wrapper").hide();
    } else {
        $("#login-form-wrapper").show();
    }

    // Login functionality
    $("#login-button").on("click", function (event) {
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: BASE_URL + "login",
        }).done(function (data) {
            token = data["token"];
            localStorage.setItem("token", token);
            $("#login-form-wrapper").hide();
            alert("Successfully logged in!");
        }).fail(function () {
            alert("Failed to login!");
        });
    });

    // Create question functionality
    $("#create-button").on("click", function (e) {
        e.preventDefault();

        let title = $("#title").val();
        let content = $("#content").val();
        let author = $("#author").val();

        if (!title || !content || !author) {
            alert("Please fill in all fields");
            return;
        }

        $.ajax({
            type: "POST",
            url: BASE_URL + "question",
            headers: {
                "Authorization": "Token: " + token
            },
            data: {
                title: title,
                content: content,
                author: author
            }
        }).done(function () {
            alert("Question created successfully!");
            location.reload();
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                alert("Please log in first!");
            } else {
                alert("Failed to create question!");
            }
        });
    });

    // Delete question functionality
    $(".delete-button").on("click", function () {
        let confirmed = confirm("Are you sure you want to delete this question?");
        let questionId = $(this).data("id");

        if (confirmed) {
            $.ajax({
                type: "DELETE",
                url: BASE_URL + "question/" + questionId,
                headers: {
                    "Authorization": "Token: " + token
                }
            }).done(function () {
                alert("Question deleted successfully!");
                location.reload();
            }).fail(function (xhr) {
                if (xhr.status === 401) {
                    alert("Please log in first!");
                } else {
                    alert("Failed to delete question!");
                }
            });
        }
    });
});