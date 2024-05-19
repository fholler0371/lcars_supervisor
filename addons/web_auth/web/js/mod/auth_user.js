define([], function() {
    window.modul['auth_user'] = {
        modul: true,
        icon: '/img/mdi/account.svg',
        label: 'Nutzereinstellungen',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['auth_user']
            if (!($('#content_modul_auth_user').length)) {
                var html = '<div id="content_modul_auth_user" class="content_modul jqx-widget-content-material modul_main_base"></div>'
                $(".main_content").append(html)
                require(['jqxinput', 'jqxbutton', 'jqxpassword'], function() {
                    html = '<table style="margin: 30px;"><tr><td><input id="content_modul_auth_user_label" type="text" autocomplete="label" required/>'
                    html += '</td><td width="20px"></td><td><input type="button" value="Namen senden" id="send_label" /></td></tr>'
                    html += '<tr height="50px"></tr><tr><td><input id="content_modul_auth_user_password_o" type="password" autocomplete="password" required/><td>'
                    html += '<td><input type="button" value="Passwort ändern" id="send_new_password" /></td>'
                    html += '</tr><tr height="20px"></tr><tr><td><input id="content_modul_auth_user_password_n" type="password" autocomplete="password_new" required/>'
                    html += '<td></tr><tr height="20px"></tr><tr><td>'
                    html += '<input id="content_modul_auth_user_password_n2" type="password" autocomplete="password_new2" required/>'
                    html += '<td></tr></table>'
                    $('#content_modul_auth_user').append(html)
                    $("#content_modul_auth_user_label").jqxInput({placeHolder: "Anzeigename", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#send_label").jqxButton({ width: 140, height: 40, theme: 'material' })
                                    .on('click', self.click_send_label)
                    $("#content_modul_auth_user_password_o").jqxPasswordInput({placeHolder: "aktuelles Passwort", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#content_modul_auth_user_password_n").jqxPasswordInput({placeHolder: "neues Passwort", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#content_modul_auth_user_password_n2").jqxPasswordInput({placeHolder: "Wiederholung", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#send_new_password").jqxButton({ width: 140, height: 40, theme: 'material' })
                                           .on('click', self.click_send_password)
                })
            } 
            $('#content_modul_auth_user').show()
        },
        show: function () {
            let self = window.modul['auth_user']
            window.modul['helper'].activate('auth_user', self.label)
            self.set_content()
            require(['jqxinput'], function() {
                window.api_call(url='user/get_label').then(resp => {
                    if (resp.ok) {
                        $("#content_modul_auth_user_label").jqxInput('val', resp.label)
                    } else {
                        notification.show('error', 'Konnte den Anmzeigename nicht laden')
                    }
                })
            })
        },
        stop: function() {
        
        },
        click_send_label() {
            window.api_call(url='user/set_label', data={label: $("#content_modul_auth_user_label").jqxInput('val')}).then(resp => {
                if (resp.ok) {
                    notification.show('info', 'Anzeigenamen gespeichert')
                } else {
                    notification.show('error', 'Anzeigenamen nicht gespeichert')
                }
            })
        },
        click_send_password : function() {
            let data={
                password : $("#content_modul_auth_user_password_o").jqxPasswordInput('val'), 
                password_new : $("#content_modul_auth_user_password_n").jqxPasswordInput('val'), 
                password_repeat : $("#content_modul_auth_user_password_n2").jqxPasswordInput('val') 
            }
            window.api_call(url='user/set_password', data).then(resp => {
                if (resp.ok) {
                    notification.show('info', 'Passwort geändert')
                } else {
                    notification.show('error', 'Passwort nicht geändert')
                }
            })
        }
    }
    window.modul['auth_user'].init()
});