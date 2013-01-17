class SessionStateUI

    constructor: (@conn) ->
        session_states = """
        <div class="btn-group">
            <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                <span class="state"></span>
                <span class="caret"></span>
            </a>
            <ul class="dropdown-menu right-align-dropdown">
                <li><a class="become-available" href="#">Available</a></li>
                <li><a class="become-busy" href="#">Busy</a></li>
                <li><a class="become-invisible" href="#">Invisible</a></li>
                <li><a class="sign-off" href="#">Sign off</a></li>
            </ul>
        </div>
            """
        $('.session-state').html(session_states)
        $('.session-state .become-available').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_available')
        $('.session-state .become-busy').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_busy')
        $('.session-state .become-invisible').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_invisible')
        $('.session-state .sign-off').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_sign_off')

    set_available: ->
        $('.session-state .state').html('Available')
        $('.session-state .btn').addClass('btn-success')

    set_busy: ->
        $('.session-state .state').html('Busy')
        $('.session-state .btn').addClass('btn-danger')

    set_invisible: ->
        $('.session-state .state').html('Invisible')
        $('.session-state .btn').addClass('btn-inverse')

    set_signed_off: ->
        $('.session-state .state').html('Signed off')


class ChatParticipantList

    constructor: (connection, user_chat_statuses) ->
        @user_list = (ucs.user for ucs in user_chat_statuses when ucs.user.username != connection.chat_session.username)

    render: =>
        chat_users_el = "<ul class=\"chat-participant-list unstyled\">"
        chat_users_el = "#{chat_users_el}#{("<li class = \"#{user.status}\">#{user.username}</li>" for user in @user_list).join('')}"
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
            if @chat_session.status == 1
                @ui_available()
            if @chat_session.status == 2
                @ui_invisible()
            if @chat_session.status == 3
                @ui_busy()
            @chat_users = chat_users
            @update_user_list_ui(chat_users)
            @update_chat_list_ui(chats)

        @conn.on 'disconnect', (data) =>
            @debug_log('Disconnect')
            @conn = null

        @conn.on 'ev_user_became_available', (username, chat_users) =>
            @debug_log("#{username} became available.")
            @chat_users = chat_users
            @update_user_list_ui(chat_users)

        @conn.on 'ev_user_became_busy', (username, chat_users) =>
            @debug_log("#{username} became busy.")
            @chat_users = chat_users
            @update_user_list_ui(chat_users)

        @conn.on 'ev_user_signed_off', (username, chat_users) =>
            @debug_log("#{username} signed off.")
            @chat_users = chat_users
            @update_user_list_ui(chat_users)

        @conn.on 'ev_chat_created', (chat) =>
            @update_chat_ui(chat)

        @conn.on 'ev_you_were_added', (chat) =>
            @update_chat_ui(chat)

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
        session_state = new SessionStateUI(@conn)
        session_state.set_signed_off()

    ui_available: =>
        $chat_window = $('.chat-window')
        $chat_window.show()
        session_state = new SessionStateUI(@conn)
        session_state.set_available()

    ui_busy: =>
        $chat_window = $('.chat-window')
        $chat_window.show()
        session_state = new SessionStateUI(@conn)
        session_state.set_busy()

    ui_invisible: =>
        $chat_window = $('.chat-window')
        $chat_window.show()
        session_state = new SessionStateUI(@conn)
        session_state.set_invisible()

    update_user_list_ui: (users) =>
        $('.users .user-list').empty()
        (@user_list_add_user(user) for user in users)

    user_list_add_user: (user) =>
        $user_list = $('.users .user-list')
        $user_el = $("<li class=\"#{user.status}\"><a href=\"#\"><i class=\"icon-user\"></i> #{user.username}</a></li>")
        $user_list.append($user_el)
        $user_el.on 'click', (e) =>
            e.preventDefault()
            @conn.emit('req_chat_create', user.username)

    update_chat_list_ui: (chats) =>
        $('.chat-list').empty()
        (@update_chat_ui(chat) for chat in chats)

    update_chat_ui: (chat) =>
        $chat_el = $("""
        <div id=\"chat-#{chat.uuid}\" class="chat well well-small">
            <div class="chat-header toggle-active clearfix"></div>
        </div>""")

        # append participant list to chat header
        chat_participant_list = new ChatParticipantList(this, chat.user_chat_statuses)
        @chat_users_lists[chat.uuid] = chat_participant_list
        $chat_el.find('.chat-header').append(chat_participant_list.render())

        # append chat controls to chat header
        $chat_el.find('.chat-header').after($("""
            <div class="chat-controls">
                <div class="btn-group">
                    <a class="btn btn-small dropdown-toggle btn-show-add-user-list" data-toggle="dropdown" href="#">
                        <i class="icon-plus"></i>
                    </a>
                    <ul class=\"dropdown-menu chat-user-list right-align-dropdown\"></ul>
                </div>
                <a href=\"#\" class=\"archive btn btn-small\"><i class="icon-remove"></i></a>
                <div class=\"unread-messages badge\"></div>
            </div>"""))

        # append messages
        $messages_el = $('<div class="messages"><div class="messages-inner clearfix"></div></div>')
        $chat_el.append($messages_el)

        # append new message input
        $message_input_el = $("""
        <div class="message-input input-prepend">
            <div class="add-on"><i class="icon-user"></i></div>
            <input type="text" placeholder="Type message">
        </div>""")
        $chat_el.append($message_input_el)

        $message_input = $message_input_el.find('input')
        $message_input.keypress (e) =>
            if e.which == 13 # Enter keycode
                self = $(e.target)
                e.preventDefault()
                if self.value == ''
                    return
                @conn.emit('req_message_send', self.value, chat.uuid)
                # TODO: show spinner, and use ack callback to hide the spinner
                self.value = ''

        # toggle active/deactive
        $chat_active_toggle = $chat_el.find('.toggle-active')
        $chat_active_toggle.click (e) =>
            e.preventDefault()
            if $chat_active_toggle.hasClass('js_active')
                @conn.emit('req_chat_deactivate', chat.uuid)
            else
                @conn.emit('req_chat_activate', chat.uuid)

        # prevent text selection
        $chat_active_toggle.mousedown (e) =>
            e.preventDefault()

        # show user list to add a new user to the chat
        $chat_el.find('.btn-show-add-user-list').click (e) =>
            e.preventDefault()
            @update_add_user_list(chat.uuid)

        # archive chat
        $chat_el.find('.archive').click (e) =>
            e.preventDefault()
            @conn.emit('req_chat_archive', chat.uuid)

        # append chat to chat-list
        $chat_list = $('.chat-list')
        $chat_list.append($chat_el)

        user_chat_status = @get_user_chat_status(chat.user_chat_statuses)
        if user_chat_status.status == 'active'
            @ui_chat_activate(chat.uuid)
        else if user_chat_status.status == 'inactive'
            @ui_chat_deactivate(chat.uuid)
            @ui_chat_set_unread_messages(chat.uuid, user_chat_status.unread_messages)
        if chat.messages.length > 0
            @update_chats_chat_messages_ui(chat.messages)

    get_user_chat_status: (user_chat_statuses) =>
        self = this
        (ucs for ucs in user_chat_statuses when ucs.user.username == self.chat_session.username)[0]

    ui_chat_activate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find('.toggle-active')
        toggle.addClass('js_active')

        # show messages
        chat.find('.messages').show()
        chat.find('.message-input').show()
        @ui_chat_clear_unread_messages(chat_uuid)
        @ui_chat_scroll_down(chat_uuid)

    ui_chat_deactivate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find('.toggle-active')
        toggle.removeClass('js_active')

        # hide messages
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

    ui_chat_clear_unread_messages: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        chat.find('.unread-messages').html('')

    ui_chat_archive: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        chat.remove()

    update_chats_chat_messages_ui: (messages) =>
        (@update_chats_chat_messages_message_ui(message) for message in messages)
        @ui_chat_scroll_down(messages[0].chat__uuid)

    update_chats_chat_messages_message_ui: (message) =>
        $chat_messages_el = $("#chat-#{message.chat__uuid} .messages-inner")
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
        $wpr = $("#chat-#{chat_uuid} .messages")
        $msgs = $wpr.find('.messages-inner')
        if not animate
            $wpr.scrollTop($msgs.outerHeight())
        else
            $wpr.animate
                scrollTop: $msgs.outerHeight(), 1000

    ui_animate_new_message: (chat_uuid) =>
        @ui_chat_scroll_down(chat_uuid, animate=true)

    update_add_user_list: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        $chat_user_list = chat.find('.chat-controls .chat-user-list')
        $chat_user_list.empty()
        ($chat_user_list.append("<li><a href=\"#\" class=\"user-add\" data-username=\"#{user.username}\"><i class=\"icon-user\"></i> #{user.username}</a></li>") for user in @chat_users)
        $chat_user_list.on 'click', '.user-add', (e) =>
            e.preventDefault()
            @conn.emit('req_chat_add_user', chat_uuid, $(e.target).data('username'))

$(->
    chat = new Chat()
    chat.init()
)
