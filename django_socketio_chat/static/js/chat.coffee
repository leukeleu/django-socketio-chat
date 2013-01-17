class UserState
    session_state_el = null

    constructor: (@conn) ->
        @session_state_el = $('.session-state')

        session_state_dropdown = """
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
        </div>"""

        @session_state_el.html(session_state_dropdown)

        session_state_dropdown.find('.become-available').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_available')
        session_state_dropdown.find('.become-busy').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_busy')
        session_state_dropdown.find('.become-invisible').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_become_invisible')
        session_state_dropdown.find('.sign-off').click (e) =>
            e.preventDefault()
            @conn.emit('req_user_sign_off')

    set_available: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Available')
        @session_state_el.find('.btn').addClass('btn-success')

    set_busy: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Busy')
        @session_state_el.find('.btn').addClass('btn-danger')

    set_invisible: =>
        $chat_window = $('.chat-window')
        $chat_window.show()

        @session_state_el.find('.state').html('Invisible')
        @session_state_el.find('.btn').addClass('btn-inverse')

    set_signed_off: =>
        $chat_window = $('.chat-window')
        $chat_window.hide()

        @session_state_el.find('.state').html('Signed off')


class UserList
    conn = null
    user_list_el = null

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
    participant_list_el = null

    constructor: (@conn, chat_el, users) ->
        @participant_list_el = $("<ul class=\"participant-list unstyled\" />")
        @set_participant_list(users)

        chat_el.find('.chat-header').append(participant_list_el)

    set_participant_list: (users) =>
        # TODO: exclude yourself from participant list
        # users = (ucs.user for ucs in user_chat_statuses when ucs.user.username != @conn.chat_session.username)

        @participant_list_el.empty()

        for user in users
            $user_el = $("<li class=\"#{user.status}\">#{user.username}</li>")
            @participant_list_el.append($user_el)


class Chat
    chat_el = null
    participant_list = null

    constructor: (@conn, chat) ->
        @chat_el = $("""
        <div id=\"chat-#{chat.uuid}\" class="chat well well-small">
            <div class="chat-header toggle-active clearfix"></div>
        </div>""")

        # append participant list to chat header
        @participant_list = new ParticipantList(@conn, @chat_el, chat.users)

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

        $message_input = $message_input_el.find('input')
        self = this
        $message_input.keypress (e) ->
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

        # prevent text selection
        $chat_active_toggle.mousedown (e) =>
            e.preventDefault()

        # show user list to add a new user to the chat
        @chat_el.find('.btn-show-add-user-list').click (e) =>
            e.preventDefault()
            @update_add_user_list(chat.uuid)

        # archive chat
        @chat_el.find('.archive').click (e) =>
            e.preventDefault()
            @conn.emit('req_chat_archive', chat.uuid)

        # append chat to chat-list
        $chat_list = $('.chat-list')
        $chat_list.append(@chat_el)

        user_chat_status = @get_user_chat_status(chat.user_chat_statuses)
        if user_chat_status.status == 'active'
            @ui_chat_activate(chat.uuid)
        else if user_chat_status.status == 'inactive'
            @ui_chat_deactivate(chat.uuid)
            @ui_chat_set_unread_messages(chat.uuid, user_chat_status.unread_messages)
        if chat.messages.length > 0
            @update_chats_chat_messages_ui(chat.messages)

    add_message: (message, user_chat_statuses) =>


    get_user_chat_status: (user_chat_statuses) =>
        self = this
        (ucs for ucs in user_chat_statuses when ucs.user.username == self.chat_session.username)[0]

    activate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find('.toggle-active')
        toggle.addClass('js_active')

        # show messages
        chat.find('.messages').show()
        chat.find('.message-input').show()
        @ui_chat_clear_unread_messages(chat_uuid)
        @ui_chat_scroll_down(chat_uuid)

    deactivate: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        toggle = chat.find('.toggle-active')
        toggle.removeClass('js_active')

        # hide messages
        chat.find('.messages').hide()
        chat.find('.message-input').hide()

    archive: (chat_uuid) =>
        chat = $("#chat-#{chat_uuid}")
        chat.remove()

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


class ChatApp
    chat_session = null
    conn = null
    user_state = null
    user_list = null
    chats = {}

    init: =>
        @connect()
        @user_state = new UserState(@conn)
        @user_list = new UserList(@conn)

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

            # init all chats
            for chat in chats
                @chats[chat.uuid] = new Chat(@conn, chat)

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
            @chats[chat.uuid] = new Chat(@conn, chat)

        @conn.on 'ev_you_were_added', (chat) =>
            @chats[chat.uuid] = new Chat(@conn, chat)

        @conn.on 'ev_chat_user_added', (chat_uuid, username, users) =>
            # TODO: remove username arg
            @chats[chat_uuid].participant_list.set_participant_list(users)

        @conn.on 'ev_message_sent', (message, user_chat_statuses) =>
            # TODO: cleanup user_chat_statuses (unread messages)
            @chats[message.chat_uuid].add_message(message, user_chat_statuses)

        @conn.on 'ev_chat_activated', (chat_uuid) =>
            @chats[chat_uuid].activate()

        @conn.on 'ev_chat_deactivated', (chat_uuid) =>
            @chats[chat_uuid].deactivate()

        @conn.on 'ev_chat_archived', (chat_uuid) =>
            @chats[chat_uuid].archive()


$(->
    chat_app = new ChatApp()
    chat_app.init()
)
