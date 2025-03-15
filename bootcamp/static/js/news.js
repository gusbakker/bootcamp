$(function () {
    function hide_stream_update() {
        $(".stream-update").hide();
    };

    function getCookie(name) {
        // Function to get any cookie available in the session.
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    function csrfSafeMethod(method) {
        // These HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    var csrftoken = getCookie('csrftoken');
    var page_title = $(document).attr("title");

    // This sets up every ajax call with proper headers.
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Focus on the modal input by default.
    $('#newsFormModal').on('shown.bs.modal', function () {
        $('#newsInput').trigger('focus')
    });

    $('#newsThreadModal').on('shown.bs.modal', function () {
        $('#replyInput').trigger('focus')
    });

    // Counts textarea characters to provide data to user.
    $("#newsInput").keyup(function () {
        var charCount = $(this).val().length;
        $("#newsCounter").text(280 - charCount);
    });

    $("#replyInput").keyup(function () {
        var charCount = $(this).val().length;
        $("#replyCounter").text(280 - charCount);
    });

    $("input, textarea").attr("autocomplete", "off");

    var postNewsForm = $('#postNewsForm');
    $("#postNews").click(function () {
        var formData = new FormData(postNewsForm[0]);
        // Ajax call after pushing button, to register a News object.
        var last_news = $(".stream li:first-child").attr("news-pk");
        if (last_news == undefined) {
            last_news = "0";
        }
        $("#postNewsForm input[name='last_news']").val(last_news);
        $.ajax({
            url: '/news/post-news/',
            type: 'POST',
            data: formData,
            async: false,
            cache: false,
            contentType: false,
            enctype: "multipart/form-data",
            processData: false,
            success: function (data) {
                $("ul.stream").prepend(data);
                $("#newsInput").val("");
                $("#newsFormModal").modal("hide");
                hide_stream_update();
            },
            error: function (data) {
                alert(data.responseText);
            },
        });
    });

    // Super enhanced debugging for delete functionality
    $("ul.stream").on("click", ".remove-news", function (e) {
        e.preventDefault();

        // Find the parent li
        var li = $(this).closest("li.infinite-item");

        // Debug output for the li
        console.log("Parent li element:", li);
        console.log("Parent li HTML:", li.prop('outerHTML'));

        // Try multiple methods to get the news ID
        var news_id = li.attr("news-id");
        var data_news_id = li.data("news-id");
        var news_uuid_attr = li.attr("data-news-uuid");

        console.log("All possible IDs - attr news-id:", news_id);
        console.log("All possible IDs - data news-id:", data_news_id);
        console.log("All possible IDs - attr data-news-uuid:", news_uuid_attr);

        // Use the first available ID
        var news = news_id || data_news_id || news_uuid_attr;

        if (!news) {
            console.error("Could not find news ID. Please check the HTML structure.");
            alert("Error: Could not identify the post to delete.");
            return;
        }

        console.log("Using news ID for deletion:", news);

        // Ask for confirmation
//        if (!confirm("Are you sure you want to delete this post?")) {
//            return;
//        }

        $.ajax({
            url: '/news/remove/',
            data: {
                'news': news
            },
            type: 'post',
            cache: false,
            success: function (data) {
                console.log("Delete successful:", data);
                $(li).fadeOut(400, function () {
                    $(li).remove();
                });
            },
            error: function(xhr, status, error) {
                console.error("Delete failed:", status, error);
                console.error("Response text:", xhr.responseText);
                console.error("Status code:", xhr.status);
                console.error("Ready state:", xhr.readyState);
                console.error("Complete XHR object:", xhr);

                alert("Error deleting post. Please try again or contact support.");
            }
        });
    });

    $("#replyNews").click(function () {
        // Ajax call to register a reply to any given News object.
        $.ajax({
            url: '/news/post-comment/',
            data: $("#replyNewsForm").serialize(),
            type: 'POST',
            cache: false,
            success: function (data) {
                $("#replyInput").val("");
                $("#newsThreadModal").modal("hide");
            },
            error: function (data) {
                alert(data.responseText);
            },
        });
    });

    $("ul.stream").on("click", ".like", function () {
        // Ajax call on action on like button.
        var li = $(this).closest("li");
        var news = $(li).attr("news-id");
        payload = {
            'news': news
        }
        $.ajax({
            url: '/news/like/',
            data: payload,
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like .like-count", li).text(data.likes);
                if ($(".like .heart", li).hasClass("fa fa-heart")) {
                    $(".like .heart", li).removeClass("fa fa-heart");
                    $(".like .heart", li).addClass("fa fa-heart-o");
                } else {
                    $(".like .heart", li).removeClass("fa fa-heart-o");
                    $(".like .heart", li).addClass("fa fa-heart");
                }
            }
        });
        return false;
    });

    $("ul.stream").on("click", ".comment", function () {
        // Ajax call to request a given News object detail and thread, and to
        // show it in a modal.
        var post = $(this).closest(".news-body");
        var news = $(post).closest("li").attr("news-id");
        $("#newsThreadModal").modal("show");
        $.ajax({
            url: '/news/get-thread/',
            data: {'news': news},
            cache: false,
            beforeSend: function () {
                $("#threadContent").html("<li class='loadcomment'><img src='/static/img/loading.gif'></li>");
            },
            success: function (data) {
                $("input[name=parent]").val(data.uuid)
                $("#newsContent").html(data.news);
                $("#threadContent").html(data.thread);
            }
        });
        return false;
    });
});