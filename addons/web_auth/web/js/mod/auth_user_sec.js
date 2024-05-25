define([], function() {
    window.modul['auth_user_sec'] = {
        modul: true,
        icon: '/img/mdi/account-lock.svg',
        label: 'Nutzereinstellungen',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['auth_user_sec']
            if (!($('#content_modul_auth_user_sec').length)) {
                var html = '<div id="content_modul_auth_user_sec" class="content_modul jqx-widget-content-material modul_main_base"></div>'
                $(".main_content").append(html)
                require(['jqxinput', 'jqxbutton'/*, 'jqxpassword'*/], function() {
                    html = '<table style="margin: 30px;"><tr><td><input id="content_modul_auth_user_sec_mail" type="text" autocomplete="mail" required/>'
                    html += '</td><td width="20px"></td><td><input type="button" value="Adresse senden" id="send_label" /></td></tr>'
                    /*html += '<tr height="50px"></tr><tr><td><input id="content_modul_auth_user_sec_password_o" type="password" autocomplete="password" required/><td>'
                    html += '<td><input type="button" value="Passwort ändern" id="send_new_password" /></td>'
                    html += '</tr><tr height="20px"></tr><tr><td><input id="content_modul_auth_user_sec_password_n" type="password" autocomplete="password_new" required/>'
                    html += '<td></tr><tr height="20px"></tr><tr><td>'
                    html += '<input id="content_modul_auth_user_sec_password_n2" type="password" autocomplete="password_new2" required/>'
                    html += '<td></tr>'*/
                    html += '</table>'
                    $('#content_modul_auth_user_sec').append(html)
                    $("#content_modul_auth_user_sec_mail").jqxInput({placeHolder: "E-Mail", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#send_label").jqxButton({ width: 140, height: 40, theme: 'material' })
                                    .on('click', self.click_send_mail)
                    /*$("#content_modul_auth_user_sec_password_o").jqxPasswordInput({placeHolder: "aktuelles Passwort", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#content_modul_auth_user_sec_password_n").jqxPasswordInput({placeHolder: "neues Passwort", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#content_modul_auth_user_sec_password_n2").jqxPasswordInput({placeHolder: "Wiederholung", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#send_new_password").jqxButton({ width: 140, height: 40, theme: 'material' })
                                           .on('click', self.click_send_password)*/
                })
            } 
            $('#content_modul_auth_user_sec').show()
        },
        show: function () {
            let self = window.modul['auth_user_sec']
            window.modul['helper'].activate('auth_user_sec', self.label)
            self.set_content()
            require(['jqxinput'], function() {
                window.api_call(url='user/get_mail').then(resp => {
                    if (resp.ok) {
                        $("#content_modul_auth_user_sec_mail").jqxInput('val', resp.mail)
                    } else {
                        notification.show('error', 'Email nicht laden')
                    }
                })
            })
        },
        stop: function() {
        
        },
        click_send_mail() {
            window.api_call(url='user/set_mail', data={mail: $("#content_modul_auth_user_sec_mail").jqxInput('val')}).then(resp => {
                if (resp.ok) {
                    notification.show('info', 'E-Mail gespeichert')
                } else {
                    notification.show('error', 'E-Mail nicht gespeichert')
                }
            })
        }/*,
        click_send_password : function() {
            let data={
                password : $("#content_modul_auth_user_sec_password_o").jqxPasswordInput('val'), 
                password_new : $("#content_modul_auth_user_sec_password_n").jqxPasswordInput('val'), 
                password_repeat : $("#content_modul_auth_user_sec_password_n2").jqxPasswordInput('val') 
            }
            window.api_call(url='user/set_password', data).then(resp => {
                if (resp.ok) {
                    notification.show('info', 'Passwort geändert')
                } else {
                    notification.show('error', 'Passwort nicht geändert')
                }
            })
        }*/
    }
    window.modul['auth_user_sec'].init()
});