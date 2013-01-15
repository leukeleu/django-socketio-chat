class ChatUserList

    constructor: (user_chat_statuses) ->
        @user_list = (ucs.user__username for ucs in user_chat_statuses)

    render: =>
        chat_users_el = "<ul class=\"chat-users unstyled\">"
        chat_users_el = "#{chat_users_el}#{("<li>#{username}</li>" for username in @user_list).join('')}"
        chat_users_el = "#{chat_users_el}</ul>"
        return chat_users_el

    append: (username) =>
        @user_list.push(username)


class Chat
    chat_session = null
    conn = null

    init: =>
        @connect()
        @chat_users_lists = {}

    debug_log: (msg) ->
        control = $('.debug-log')
        now = new Date()
        control.append(now.toLocaleTimeString() + ': ' + msg + '<br/>')

    connect: ->
        @conn = io.connect 'https://' + window.location.host,
        'force_new_connection': false
        'rememberTransport': true
        'resource': 'chat/socket.io'

        @debug_log('Connecting...')

        @conn.on 'connect', =>
            @debug_log('Connected')

        @conn.on 'ev_chat_session_status', (chat_session) =>
            #  Not signed in yet
            @chat_session = chat_session
            if @chat_session.status == 0
                @ui_signed_off()

        @conn.on 'ev_data_update', (chat_session, chat_users, chats) =>
            # You are signed in
            @chat_session = chat_session
            @ui_signed_in()
            @chat_users = chat_users
            @update_users_ui(chat_users)
            @update_chats_ui(chats)

        @conn.on 'disconnect', (data) =>
            @debug_log('Disconnect')
            @conn = null

        @conn.on 'ev_user_signed_in', (username, chat_users) =>
            @debug_log("#{username} signed in.")
            @chat_users = chat_users
            @update_users_ui(chat_users)

        @conn.on 'ev_user_signed_off', (username, chat_users) =>
            @debug_log("#{username} signed off.")
            @chat_users = chat_users
            @update_users_ui(chat_users)

        @conn.on 'ev_chat_created', (chat) =>
            @update_chats_chat_ui(chat)

        @conn.on 'ev_you_were_added', (chat) =>
            @update_chats_chat_ui(chat)

        @conn.on 'ev_chat_user_added', (chat_uuid, username) =>
            chat_user_list = @chat_users_lists[chat_uuid]
            chat_user_list.append(username)
            chat = $("#chat-#{chat_uuid}")
            chat.find('.chat-users').html(chat_user_list.render())

        @conn.on 'ev_message_sent', (message, user_chat_statuses) =>
            @update_chats_chat_messages_message_ui(message)
            @ui_animate_new_message(message.chat__uuid)
            user_chat_status = @get_user_chat_status(user_chat_statuses)
            @ui_chat_set_unread_messages(message.chat__uuid, user_chat_status.unread_messages)

        @conn.on 'ev_chat_activated', (chat_uuid) =>
            @ui_chat_activate(chat_uuid)

        @conn.on 'ev_chat_deactivated', (chat_uuid) =>
            @ui_chat_deactivate(chat_uuid)

        @conn.on 'ev_chat_archived', (chat_uuid) =>
            @ui_chat_archive(chat_uuid)

    ui_signed_off: ->
        $('.chat-window').hide()
        $('.chat-session-state').html('<h1>Signed off</h1><a class="sign-in" href="#">Sign in</a>')
        $('.sign-in').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_sign_in')

    ui_signed_in: =>
        $chat_window = $('.chat-window')
        $chat_window.show()
        $('.chat-session-state').html('<h1>Signed in</h1><a class="sign-off" href="#">Sign off</a>')
        $('.sign-off').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_sign_off')

    update_users_ui: (users) =>
        $('.user-list').empty()
        (@ui_add_user(user) for user in users)

    ui_add_user: (user) =>
        $user_list = $('.user-list')
        $user_el = $("<li class=\"(#{if user.is_online then 'online' else 'offline'})\"><i class=\"icon-user\"></i> <a href=\"#\">#{user.username}</a></li>")
        $user_list.append($user_el)
        $user_el.on 'click', (e) =>
            e.preventDefault()
            @conn.emit('req_chat_create', user.username)

    update_chats_ui: (chats) =>
        $('.chat-list').empty()
        (@update_chats_chat_ui(chat) for chat in chats)

    update_chats_chat_ui: (chat) =>
        chat_user_list = new ChatUserList(chat.user_chat_statuses)
        @chat_users_lists[chat.uuid] = chat_user_list
        $chat_el = $("""
        <div id=\"chat-#{chat.uuid}\" class="chat well well-small">
            <div class="clearfix">
                #{chat_user_list.render()}
                <div class="chat-controls">
                    <a href=\"#\" class=\"toggle-active btn btn-small\"></a>
                    <a href=\"#\" class=\"archive btn btn-small\">Archive</a>
                    <div class="btn-group">
                        <a class="btn list-users dropdown-toggle" data-toggle="dropdown" href="#">
                            <i class="icon-user"></i>
                            <span class="caret"></span>
                        </a>
                        <ul class=\"dropdown-menu chat-user-list unstyled\"></ul>
                    </div>
                    <span class=\"unread-messages badge\"></span>
                </div>
            </div>
        </div>""")

        $messages_el = $('<div class="wpr-messages"><div class="messages clearfix"></div></div>')
        $message_input_el = $("""
        <div class="message-input input-prepend">
            <div class="add-on"><i class="icon-user"></i></div>
            <input id="prependedInput" type="text" placeholder="Type message">
        </div>""")

        $chat_el.append($messages_el)
        $chat_el.append($message_input_el)

        $message_input = $message_input_el.find('input')
        self = this # can't use ''=>'' here, TODO find a better soulution
        $message_input.keypress (e) ->
            if e.which == 13 # Enter keycode
                e.preventDefault()
                if this.value == ''
                    return
                self.conn.emit('req_message_send', this.value, chat.uuid)
                # TODO: show spinner, and use ack callback to hide the spinner
                this.value = ''

        $chat_active_toggle = $chat_el.find('.toggle-active')
        user_chat_status = @get_user_chat_status(chat.user_chat_statuses)
        $chat_active_toggle.click (e) =>
            e.preventDefault()
            if $chat_active_toggle.hasClass('js_active')
                @conn.emit('req_chat_deactivate', chat.uuid)
            else
                @conn.emit('req_chat_activate', chat.uuid)

        $chat_el.find('.list-users').click (e) =>
            e.preventDefault()
            @list_users(chat.uuid)

        $chat_el.find('.archive').click (e) =>
            e.preventDefault()
            @conn.emit('req_chat_archive', chat.uuid)

        $chat_list = $('.chat-list')
        $chat_list.append($chat_el)

        if user_chat_status.status == 'active'
            @ui_chat_activate(chat.uuid)
        else if user_chat_status.status == 'inactive'
            @ui_chat_deactivate(chat.uuid)
            @ui_chat_set_unread_messages(chat.uuid, user_chat_status.unread_messages)
        if chat.messages.length > 0
            @update_chats_chat_messages_ui(chat.messages)

    get_user_chat_status: (user_chat_statuses) =>
        self = this
        (ucs for ucs in user_chat_statuses when ucs.user__username == self.chat_session.username)[0]

    ui_chat_activate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find(".toggle-active")
        toggle.text('Deactivate')
        toggle.addClass('js_active')
        chat.find('.messages').show()
        chat.find('.message-input').show()
        @ui_chat_clear_unread_messages(chat_uuid)
        @ui_chat_scroll_down(chat_uuid)

    ui_chat_deactivate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find(".toggle-active")
        toggle.text(' Activate')
        toggle.removeClass('js_active')
        chat.find('.messages').hide()
        chat.find('.message-input').hide()

    ui_chat_set_unread_messages: (chat_uuid, count) =>
        chat = $("#chat-#{chat_uuid}")
        unread_messages = chat.find('.unread-messages')
        if count > 0
            unread_messages
                .html(count)
                .addClass('active')
        else
            unread_messages.removeClass('active')

    ui_chat_clear_unread_messages:(chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        chat.find('.unread-messages').html('')

    ui_chat_archive: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        chat.remove()

    update_chats_chat_messages_ui: (messages) =>
        (@update_chats_chat_messages_message_ui(message) for message in messages)
        @ui_chat_scroll_down(messages[0].chat__uuid)

    update_chats_chat_messages_message_ui: (message) =>
        $chat_messages_el = $("#chat-#{message.chat__uuid} .messages")
        stamp = (timestamp) =>
            timestamp = new Date(timestamp)
            return ('0' + timestamp.getHours()).slice(-2) + ':' + ('0' + timestamp.getMinutes()).slice(-2)
        s = """
        <blockquote id=\"message-#{message.uuid}\" class="message
            #{if message.user_from__username == @chat_session.username then ' pull-right\"' else '\"'}>
            <p class="msg-body">#{message.message_body}</p>
            <small class="msg-sender-timestamp">#{message.user_from__username} - #{stamp(message.timestamp)}</small>
        </blockquote>"""
        $chat_messages_el.append($(s))

    ui_chat_scroll_down: (chat_uuid, animate=false) =>
        $wpr = $("#chat-#{chat_uuid} .wpr-messages")
        $msgs = $wpr.find('.messages')
        if not animate
            $wpr.scrollTop($msgs.outerHeight())
        else
            $wpr.animate
                scrollTop: $msgs.outerHeight(), 1000

    ui_animate_new_message: (chat_uuid) =>
        @ui_chat_scroll_down(chat_uuid, animate=true)

    list_users: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        $chat_user_list = chat.find('.chat-user-list')
        $chat_user_list.empty()
        ($chat_user_list.append("<li><i class=\"icon-user\"></> <a href=\"#\" class=\"user-add\" data-username=\"#{user.username}\">#{user.username}</a></li>") for user in @chat_users)
        $chat_user_list.on 'click', '.user-add', (e) =>
            e.preventDefault()
            @conn.emit('req_chat_add_user', chat_uuid, $(e.target).data('username'))

$(->
    chat = new Chat()
    chat.init()
)
