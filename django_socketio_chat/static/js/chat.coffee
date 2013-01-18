class UserState

    constructor: (@conn) ->
        @session_state_el = $('.session-state')

        session_state_dropdown_el = $("""
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
        </div>""")

        @session_state_el.html(session_state_dropdown_el)

        session_state_dropdown_el.find('.become-available').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_available')
        session_state_dropdown_el.find('.become-busy').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_busy')
        session_state_dropdown_el.find('.become-invisible').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_invisible')
        session_state_dropdown_el.find('.sign-off').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_sign_off')

    set_available: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Available')
        @clear_btn_classes()
        @session_state_el.find('.btn').addClass('btn-success')

    set_busy: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Busy')
        @clear_btn_classes()
        @session_state_el.find('.btn').addClass('btn-danger')

    set_invisible: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Invisible')
        @clear_btn_classes()
        @session_state_el.find('.btn').addClass('btn-inverse')

    set_signed_off: =>
        $chat_window = $('.chat-window')
        $chat_window.hide()

        @session_state_el.find('.state').html('Signed off')

    clear_btn_classes: =>
        @session_state_el.find('.btn').removeClass('btn-success btn-danger btn-inverse')


class UserList

    constructor: (@conn) ->
        @user_list_el = $('.users .user-list')

    set_user_list: (users) =>
        @user_list_el.empty()

        for user in users
            $user_el = $("""
            <li class=\"#{user.status}\">
                <a href=\"#\">
                    <i class=\"icon-user\"></i>
                    #{user.username}
                </a>
            </li>""")

            # add click event
            $user_el.click (e) =>
                e.preventDefault()
                @conn.emit('req_chat_create', user.username)

            # append user_el
            @user_list_el.append($user_el)


class ParticipantList

    constructor: (@conn, @chat_session, chat_el, user_chat_statuses) ->
        @participant_list_el = $('<ul class="participant-list unstyled" />')
        @set_participant_list(user_chat_statuses)

        chat_el.find('.chat-header').append(@participant_list_el)

    set_participant_list: (user_chat_statuses) =>
        @participant_list_el.empty()

        for user_chat_status in user_chat_statuses
            if user_chat_status.user.username != @chat_session.username
                $user_el = $("<li class=\"#{user_chat_status.user.status}\">#{user_chat_status.user.username}</li>")
                @participant_list_el.append($user_el)


class Chat

    constructor: (@conn, @chat_session, @chat) ->
        @chat_el = $("""
        <div id=\"chat-#{chat.uuid}\" class="chat well well-small">
            <div class="chat-header toggle-active clearfix"></div>
        </div>""")

        # append participant list to chat header
        @participant_list = new ParticipantList(@conn, @chat_session, @chat_el, @chat.user_chat_statuses)

        # append chat controls to chat header
        @chat_el.find('.chat-header').after($("""
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
        @chat_el.append($messages_el)

        # append new message input
        $message_input_el = $("""
        <div class="message-input input-prepend">
            <div class="add-on"><i class="icon-user"></i></div>
            <input type="text" placeholder="Type message">
        </div>""")
        @chat_el.append($message_input_el)

        self = this
        $message_input_el.find('input').keypress (e) ->
            if e.which == 13 # Enter keycode
                e.preventDefault()
                if this.value == ''
                    return
                self.conn.emit('req_message_send', this.value, chat.uuid)
                # TODO: show spinner, and use ack callback to hide the spinner
                this.value = ''

        # toggle active/deactive
        $chat_active_toggle = @chat_el.find('.toggle-active')
        $chat_active_toggle.click (e) =>
            e.preventDefault()
            if $chat_active_toggle.hasClass('js_active')
                @conn.emit('req_chat_deactivate', chat.uuid)
            else
                @conn.emit('req_chat_activate', chat.uuid)

        # prevent text selection in chat header
        $chat_active_toggle.mousedown (e) =>
            e.preventDefault()

        # show user list to add a new user to the chat click event
        @chat_el.find('.btn-show-add-user-list').click (e) =>
            e.preventDefault()
            @update_add_user_list(chat.uuid)

        # archive chat click event
        @chat_el.find('.archive').click (e) =>
            e.preventDefault()
            @conn.emit('req_chat_archive', chat.uuid)

        # append chat to chat-list
        $('.chat-list').append(@chat_el)

        if @is_active
            @activate()
        else
            @deactivate()
            @set_unread_messages(user_chat_status.unread_messages)

        # add messages
        if @chat.messages.length > 0
            for message in chat.messages
                @add_message(message)
            @ui_scroll_down()

    is_active: =>
        for ucs in @chat.user_chat_statuses
            if ucs.user.username == @chat_session.username
                return true

    add_message: (message, user_chat_statuses) =>

        stamp = (timestamp) =>
            timestamp = new Date(timestamp)
            return ('0' + timestamp.getHours()).slice(-2) + ':' + ('0' + timestamp.getMinutes()).slice(-2)

        $message_el = $("""
        <blockquote id=\"message-#{message.uuid}\" class="message
            #{if message.user_from__username == @chat_session.username then ' pull-right\"' else '\"'}>
            <p class="msg-body">#{message.message_body}</p>
            <small class="msg-sender-timestamp">#{message.user_from__username} - #{stamp(message.timestamp)}</small>
        </blockquote>""")
        @chat_el.find('.messages-inner').append($message_el)

    new_message: (message, user_chat_statuses) =>
        @add_message(message, user_chat_statuses)
        @ui_scroll_down(true)

    activate: =>
        @chat_el.find('.toggle-active').addClass('js_active')

        # show messages
        @chat_el
            .find('.messages').show()
            .find('.message-input').show()

        @set_unread_messages()
        @ui_scroll_down()

    deactivate: =>
        @chat_el.find('.toggle-active').removeClass('js_active')

        # hide messages
        @chat_el
            .find('.messages').hide()
            .find('.message-input').hide()

    archive: =>
        @chat_el.remove()

    set_unread_messages: (count=0) =>
        unread_messages = @chat_el.find('.unread-messages')
        if count > 0
            unread_messages
                .html(count)
                .addClass('active')
        else
            unread_messages
                .html('')
                .removeClass('active')

    ui_scroll_down: (animate=false) =>
        $messages_el = @chat_el.find('.messages')
        $messages_inner_el = @chat_el.find('.messages-inner')

        if animate
            $messages_el.animate
                scrollTop: $messages_inner_el.outerHeight(), 1000
        else
            $messages_el.scrollTop($messages_inner_el.outerHeight())

    update_add_user_list: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        $chat_user_list = chat.find('.chat-controls .chat-user-list')
        $chat_user_list.empty()
        ($chat_user_list.append("<li><a href=\"#\" class=\"user-add\" data-username=\"#{user.username}\"><i class=\"icon-user\"></i> #{user.username}</a></li>") for user in @chat_users)
        $chat_user_list.on 'click', '.user-add', (e) =>
            e.preventDefault()
            @conn.emit('req_chat_add_user', chat_uuid, $(e.target).data('username'))


class ChatApp

    constructor: ->
        @chat_session = null
        @chats = {}
        @connect()
        @user_state = new UserState(@conn)
        @user_list = new UserList(@conn)

    debug_log: (msg) =>
        control = $('.debug-log')
        now = new Date()
        control.append(now.toLocaleTimeString() + ': ' + msg + '<br/>')

    connect: =>
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
                @user_state.set_signed_off()

        @conn.on 'ev_data_update', (chat_session, chat_users, chats) =>
            # You are signed in
            @chat_session = chat_session
            if @chat_session.status == 1
                @user_state.set_available()
            if @chat_session.status == 2
                @user_state.set_invisible()
            if @chat_session.status == 3
                @user_state.set_busy()

            # update user list
            @user_list.set_user_list(chat_users)

            # clear chat list
            $('.chat-list').empty()

            # init all chats
            for chat in chats
                @chats[chat.uuid] = new Chat(@conn, @chat_session, chat)

        @conn.on 'disconnect', (data) =>
            @debug_log('Disconnect')
            @conn = null

        @conn.on 'ev_user_became_available', (username, users) =>
            @debug_log("#{username} became available.")
            @user_list.set_user_list(users)

        @conn.on 'ev_user_became_busy', (username, users) =>
            @debug_log("#{username} became busy.")
            @user_list.set_user_list(users)

        @conn.on 'ev_user_signed_off', (username, users) =>
            @debug_log("#{username} signed off.")
            @user_list.set_user_list(users)

        @conn.on 'ev_chat_created', (chat) =>
            @chats[chat.uuid] = new Chat(@conn, @chat_session, chat)

        @conn.on 'ev_you_were_added', (chat) =>
            @chats[chat.uuid] = new Chat(@conn, @chat_session, chat)

        @conn.on 'ev_chat_user_added', (chat_uuid, username, users) =>
            # TODO: remove username arg
            @chats[chat_uuid].participant_list.set_participant_list(users)

        @conn.on 'ev_message_sent', (message, user_chat_statuses) =>
            # TODO: cleanup user_chat_statuses (unread messages)
            @chats[message.chat__uuid].new_message(message, user_chat_statuses)

        @conn.on 'ev_chat_activated', (chat_uuid) =>
            @chats[chat_uuid].activate()

        @conn.on 'ev_chat_deactivated', (chat_uuid) =>
            @chats[chat_uuid].deactivate()

        @conn.on 'ev_chat_archived', (chat_uuid) =>
            @chats[chat_uuid].archive()


$(->
    new ChatApp()
)
