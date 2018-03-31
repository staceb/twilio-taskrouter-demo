/**
 * Copyright (c) 2018 Alex Laird.
 *
 * @author Alex Laird
 * @version 0.1.0
 */

$(function () {
    var USER;
    var CHAT_CLIENT;
    var WORKER;

    var currentChannel;
    var currentContact;

    var $chatWindow = $("#chat-window");
    var $lobbyWindow = $("#lobby-window");
    var $lobbyVideo = $("#lobby-video");
    var $messages = $("#messages");
    var $replyBox = $("#reply-box");

    function lobbyVideoCommand(command) {
        $lobbyVideo[0].contentWindow.postMessage('{"event":"command","func":"' + command + '","args":""}', '*');
    }

    function refreshToken() {
        if (WORKER) {
            console.log("Getting refresh token for worker.");

            twiltwilapi.getTwilioWorkerToken(function (data) {
                WORKER.updateToken(data.token);
            });
        }
    }

    function updateWorkerActivity(activityName) {
        WORKER.activities.fetch(
            function (error, activities) {
                for (var i = 0; i < activities.data.length; i++) {
                    if (activities.data[i].friendlyName === activityName) {
                        WORKER.update("ActivitySid", activities.data[i].sid);

                        break;
                    }
                }
            }
        );
    }

    function displayMessage(message) {
        console.log(message);

        var $time = $('<small class="pull-right time"><i class="fa fa-clock-o"></i></small>').text(message.timestamp.toLocaleString());
        var $user;
        if (message.author === USER.username) {
            $user = $('<h5 class="media-heading me"></h5>').text(USER.username + " (me)");
        } else if (message.author !== currentContact.sid) {
            $user = $('<h5 class="media-heading me"></h5>').text(message.author + " (previous agent)");
        } else {
            $user = $('<h5 class="media-heading"></h5>').text(currentContact.card);
        }
        var $body = $('<small class="col-lg-10"></small>').text(message.body);
        var $container = $('<div class="media msg">');
        $container.append($time).append($user).append($body);
        $messages.append($container);
        $messages.scrollTop($messages[0].scrollHeight);
    }

    function initChannel(channel) {
        channel.join().then(function (channel) {
            currentChannel = channel;
            twiltwilapi.getContact(function (contact) {
                currentContact = contact;

                lobbyVideoCommand('pauseVideo');
                $lobbyWindow.hide();
                $chatWindow.show();

                console.log('Joined channel ' + currentChannel.uniqueName);

                currentChannel.getMessages().then(function (messages) {
                    $.each(messages.items, function (index, message) {
                        displayMessage(message);
                    });
                });
            }, channel.uniqueName);
        });

        channel.on('messageAdded', function (message) {
            // TODO: sometimes this double posts, it seems (fine on refresh), so perhaps just filter if already seen
            displayMessage(message);
        });
    }

    function joinChannel(uniqueName) {
        var promise = CHAT_CLIENT.getChannelByUniqueName(uniqueName);
        promise.then(function (channel) {
            console.log('Found ' + channel.uniqueName + ' channel');
            console.log(channel);

            initChannel(channel);
        });
    }

    function initChat(token) {
        CHAT_CLIENT = new Twilio.Chat.Client(token);

        CHAT_CLIENT.getSubscribedChannels().then(function (channels) {
            $.each(channels.items, function (index, channel) {
                joinChannel(channel.uniqueName);
            });
        });
    }

    function initWorker(token) {
        WORKER = new Twilio.TaskRouter.Worker(token);

        WORKER.on("ready", function (worker) {
            console.log(worker.sid);
            console.log(worker.friendlyName);
            console.log(worker.activityName);
            console.log(worker.available);
            console.log(worker.attributes);

            $("#user-details-status").html(worker.activityName);
        });

        WORKER.on("activity.update", function (worker) {
            console.log(worker.sid);
            console.log(worker.friendlyName);
            console.log(worker.activityName);
            console.log(worker.available);

            $("#user-details-status").html(worker.activityName);
        });

        WORKER.on("reservation.created", function (reservation) {
            console.log(reservation.sid);
            console.log(reservation.task.sid);
            console.log(reservation.task.priority);
            console.log(reservation.task.age);
            console.log(reservation.task.attributes);

            updateWorkerActivity("Busy");

            reservation.accept();

            var chatContact = reservation.task.attributes.from;

            CHAT_CLIENT.getSubscribedChannels().then(function () {
                $messages.html("");

                joinChannel(chatContact);
            });
        });

        // Refresh token every 55 minutes
        setTimeout(refreshToken, 1000 * 60 * 55);
    }

    twiltwilapi.getUser(function (data) {
        USER = data;

        $("#user-details-username").html(USER.username);
        $.each(USER.languages, function (index, language) {
            $("#user-details-languages").append('<li><small>' + language + '</small></li>');
        });
        $.each(USER.skills, function (index, skill) {
            $("#user-details-skills").append('<li><small>' + skill + '</small></li>');
        });

        twiltwilapi.getTwilioChatToken(function (data) {
            initChat(data.token);

            twiltwilapi.getTwilioWorkerToken(function (data) {
                initWorker(data.token);
            });
        }, USER.username);
    });

    $("#send-button").on("click", function () {
        var message = $replyBox.val();

        if ($.trim(message) !== "") {
            currentChannel.sendMessage($replyBox.val(), {
                "To": currentChannel.uniqueName
            });
            $replyBox.val("").focus();
        }
    });

    $("#solve-button").on("click", function () {
        WORKER.fetchReservations(
            function (error, reservations) {
                for (i = 0; i < reservations.data.length; i++) {
                    if (reservations.data[i].task.assignmentStatus === "assigned") {
                        WORKER.completeTask(reservations.data[i].task.sid, function () {
                            $chatWindow.hide();
                            $lobbyWindow.show();
                            lobbyVideoCommand('playVideo');
                            currentChannel.leave();
                            currentChannel = null;
                            currentContact = null;

                            updateWorkerActivity("Idle");
                        });

                        break;
                    }
                }
            }
        );
    });
});
