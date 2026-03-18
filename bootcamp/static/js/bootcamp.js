/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

/* Notifications JS basic client */
$(function () {
    let emptyMessage = 'data-empty="true"';

    function updateUnreadNotifications() {
        $.ajax({
            url: '/notifications/unread-notifications/',
            cache: false,
            success: function (data) {
                var unreadNum = data.unread_notifications
                if (unreadNum != null && unreadNum > 0) {
                    if (unreadNum > 9) {
                        unreadNum = '9+'
                    }
                    $("#countnotif").text(unreadNum).removeClass("hidden");
                } else {
                    $("#countnotif").text("").addClass("hidden");
                }
            },
        });
    };

    function updateUnreadMessages() {
        $.ajax({
            url: '/messages/get-unread-messages/',
            cache: false,
            success: function (data) {
                var unreadNum = data.unread_messages
                if (unreadNum != null && unreadNum > 0) {
                    if (unreadNum > 9) {
                        unreadNum = '9+'
                    }
                    $("#countmsg").text(unreadNum).removeClass("hidden");
                } else {
                    $("#countmsg").text("").addClass("hidden");
                }
            },
        });
    };


    function update_social_activity(id_value) {
        let newsToUpdate = $("[news-id=" + id_value + "]");
        payload = {
            'id_value': id_value,
        };
        $.ajax({
            url: '/news/update-interactions/',
            data: payload,
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            },
        });
    };

    updateUnreadNotifications();
    updateUnreadMessages();

    function markUnreadAjax() {
        // Ajax request to mark as unread inside the popover
        $("ul.notif").on("click", ".pop-notification", function () {
            var li = $(this).closest("li");
            var slug = $(li).attr("notification-slug");
            $.ajax({
                url: '/notifications/mark-as-read-ajax/',
                data: {
                    'slug': slug,
                },
                type: 'post',
                cache: false,
                success: function (data) {
                    $(li).fadeOut(400, function () {
                        $(li).remove();
                        updateUnreadNotifications();
                    });
                }
            });
        });
    }

    // Click handler for Notifications Dropdown
    $("#notifications").click(function (e) {
        e.stopPropagation();
        var menu = $("#notificationsMenu");

        if (menu.hasClass("hidden") || menu.css("display") === "none") {
            // Hide other menus
            $("#profileMenu").addClass('hidden');

            // Show notifications
            menu.removeClass('hidden').css("display", "flex");

            $.ajax({
                url: '/notifications/latest-notifications/',
                beforeSend: function () {
                    $("#notificationsBody").html("<div class='py-8 flex justify-center'><div class='animate-spin rounded-full h-8 w-8 border-b-2 border-fb-primary'></div></div>");
                },
                success: function (data) {
                    $("#countnotif").text("");
                    $("#notificationsBody").html(data);
                }
            });
        } else {
            menu.addClass('hidden').css("display", "none");
        }
        return false;
    });

    // Close notifications menu when clicking outside
    $(document).on("click", function (e) {
        var menu = $("#notificationsMenu");
        if (!$(e.target).closest('#notifications').length && !$(e.target).closest('#notificationsMenu').length) {
            menu.addClass('hidden').css("display", "none");
        }
    });

    // Code block to manage WebSocket connections
    // Try to correctly decide between ws:// and wss://
    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/notifications/";
    let webSocket = new channels.WebSocketBridge();
    webSocket.connect(ws_path);

    // Helpful debugging
    webSocket.socket.onopen = function () {
        console.log("Connected to " + ws_path);
    };

    webSocket.socket.onclose = function () {
        console.error("Disconnected from " + ws_path);
    };

    // Listen the WebSocket bridge created throug django-channels library.
    webSocket.listen(function (event) {
        switch (event.key) {
            case "notification":
                updateUnreadNotifications();
                break;

            case "social_update":
                updateUnreadNotifications();
                break;

            case "message":
                if (currentUser == event.recipient) {
                    updateUnreadMessages();
                }
                break;

            case "additional_news":
                if (event.actor_name !== currentUser) {
                    $(".stream-update").show();
                }
                break;

            default:
                console.log('error: ', event);
                break;
        }
        ;
    });
});
