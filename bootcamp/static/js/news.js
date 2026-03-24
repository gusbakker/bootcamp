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

    // Focus on the modal input by default using MutationObserver since Bootstrap events are gone
    const observeModalFocus = (modalId, inputId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class' && !modal.classList.contains('hidden')) {
                        setTimeout(() => document.getElementById(inputId).focus(), 100);
                    }
                });
            }).observe(modal, { attributes: true });
        }
    };
    observeModalFocus('newsFormModal', 'newsInput');
    observeModalFocus('newsThreadModal', 'replyInput');

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
                // Hide modal gracefully
                const modal = document.getElementById("newsFormModal");
                if (modal && !modal.classList.contains("hidden")) {
                    modal.classList.add("hidden");
                    document.body.style.overflow = "auto";
                }
                hide_stream_update();
            },
            error: function (data) {
                alert(data.responseText);
            },
        });
    });

    // Intercept delete click to show modal
    $("ul.stream").on("click", ".remove-news", function (e) {
        e.preventDefault();

        // Update modal text based on whether it's a post or a comment
        var dataType = $(this).attr("data-type") || "post";
        if (dataType === "comment") {
            $("#deleteModalTitle").text("Delete Comment");
            $("#deleteModalBody").text("Are you sure you want to delete this comment? This action cannot be undone.");
        } else {
            $("#deleteModalTitle").text("Delete Post");
            $("#deleteModalBody").text("Are you sure you want to delete this post? This action cannot be undone.");
        }

        // Find the parent li
        var li = $(this).closest("li.infinite-item");

        // Try multiple methods to get the news ID
        var news_id = li.attr("news-id");
        var data_news_id = li.data("news-id");
        var news_uuid_attr = li.attr("data-news-uuid");

        // Use the first available ID
        var news = news_id || data_news_id || news_uuid_attr;

        if (!news) {
            alert("Error: Could not identify the post to delete.");
            return;
        }

        // Store the ID in the modal and explicitly clear older pending markers
        $("#deletePostId").val(news);
        $("li.pending-delete").removeClass("pending-delete");
        li.addClass("pending-delete"); // Marking it so the confirm button knows which DOM element to remove

        // Show modal gracefully
        const modal = document.getElementById("newsDeleteModal");
        if (modal) {
            modal.classList.remove("hidden");
            document.body.style.overflow = "hidden";
        }
    });

    // Handle actual deletion after confirmation
    $("#confirmDeletePostBtn").click(function () {
        var news = $("#deletePostId").val();
        var li = $("li.pending-delete");

        $.ajax({
            url: '/news/remove/',
            data: {
                'news': news
            },
            type: 'post',
            cache: false,
            success: function (data) {
                // Hide modal gracefully
                const modal = document.getElementById("newsDeleteModal");
                if (modal && !modal.classList.contains("hidden")) {
                    modal.classList.add("hidden");
                    document.body.style.overflow = "auto";
                }

                $(li).fadeOut(400, function () {
                    $(li).remove();
                });
            },
            error: function (xhr, status, error) {
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
                const modal = document.getElementById("newsThreadModal");
                if (modal && !modal.classList.contains("hidden")) {
                    modal.classList.add("hidden");
                    document.body.style.overflow = "auto";
                }
            },
            error: function (data) {
                alert(data.responseText);
            },
        });
    });

    $("ul.stream").on("click", ".like", function (e) {
        e.preventDefault();
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
                var likeBtn = $(".like", li);

                // Update like count: post uses .reaction-counts, comment uses .like-count inside btn
                if ($(".reaction-counts .like-count", li).length > 0) {
                    $(".reaction-counts .like-count", li).text(data.likes);
                } else {
                    $(".like-count", likeBtn).text(data.likes);
                }

                var heartIcon = $(".heart", likeBtn);
                if (heartIcon.length > 0) {
                    // Post like button toggle
                    if (heartIcon.hasClass("fa-solid")) {
                        heartIcon.removeClass("fa-solid text-fb-primary").addClass("fa-regular");
                        likeBtn.find("span").removeClass("text-fb-primary");
                    } else {
                        heartIcon.removeClass("fa-regular").addClass("fa-solid text-fb-primary");
                        likeBtn.find("span").addClass("text-fb-primary");
                    }
                } else {
                    // Comment like button toggle
                    var likeText = likeBtn.find("span").not(".like-count");
                    if (likeText.hasClass("text-fb-primary")) {
                        likeText.removeClass("text-fb-primary");
                        likeText.addClass("text-fb-lightMuted dark:text-fb-muted");
                    } else {
                        likeText.removeClass("text-fb-lightMuted dark:text-fb-muted");
                        likeText.addClass("text-fb-primary");
                    }
                }
            }
        });
        return false;
    });

    $("ul.stream").on("click", ".comment", function () {
        // Ajax call to request a given News object detail and thread, and to
        // show it in a modal.
        var post = $(this).closest(".news-body");
        if (post.length === 0) post = $(this).closest(".news-card");
        var news = $(this).closest("li").attr("news-id");

        // Show modal gracefully
        const modal = document.getElementById("newsThreadModal");
        if (modal && modal.classList.contains("hidden")) {
            modal.classList.remove("hidden");
            document.body.style.overflow = "hidden";
        }

        $.ajax({
            url: '/news/get-thread/',
            data: { 'news': news },
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

    // Likers Dropdown Logic
    window.showLikers = function(newsId) {
        const dropdown = $(`#likers-dropdown-${newsId}`);
        const list = $(`#likers-list-${newsId}`);

        if (!dropdown.hasClass('hidden')) {
            dropdown.addClass('hidden');
            return;
        }

        // Hide all other likers dropdowns first
        $('.news-likers-list').parent().addClass('hidden');

        $.ajax({
            url: '/news/get-likers/',
            data: { 'news': newsId },
            type: 'GET',
            cache: false,
            beforeSend: function() {
                list.html('<div class="p-4 flex justify-center"><div class="animate-spin rounded-full h-5 w-5 border-b-2 border-fb-primary"></div></div>');
                dropdown.removeClass('hidden');
            },
            success: function(data) {
                list.empty();
                if (data.length > 0) {
                    data.forEach(user => {
                        const html = `
                            <a href="${user.url}" class="flex items-center gap-2 p-2 hover:bg-fb-lightSurfaceHover dark:hover:bg-fb-surfaceHover rounded-lg transition text-decoration-none">
                                <img src="${user.image}" class="w-8 h-8 rounded-full object-cover">
                                <div class="flex flex-col min-w-0">
                                    <span class="font-bold text-xs text-fb-lightText dark:text-fb-text truncate">${user.name}</span>
                                    <span class="text-[10px] text-fb-lightMuted dark:text-fb-muted truncate">@${user.username}</span>
                                </div>
                            </a>
                        `;
                        list.append(html);
                    });
                } else {
                    list.html('<div class="p-4 text-center text-xs text-fb-lightMuted dark:text-fb-muted">No likes yet</div>');
                }
            }
        });
    };

    // Close likers dropdown when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('[id^="likers-dropdown-"]').length && !$(e.target).closest('div[onclick^="showLikers"]').length) {
            $('[id^="likers-dropdown-"]').addClass('hidden');
        }
    });

    // Handle comment click from summary text
    $("ul.stream").on("click", ".comment-trigger", function() {
        $(this).closest("li").find(".comment").trigger("click");
    });
});