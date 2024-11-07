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
                    html += '</td><td width="20px"></td><td><input type="button" value="Adresse senden" id="content_modul_auth_user_sec_send_label" /></td></tr>'
                    html += '<tr height="20px"></tr>'
                    html += '<tr height="50px"></tr><tr><td id="content_modul_auth_user_sec_totp"></td><td></td>'
                    html += '<td><input type="button" value="TOTP erstellen" id="content_modul_auth_user_sec_get_totp" /></td>'
                    html += '</table>'
                    $('#content_modul_auth_user_sec').append(html)
                    $("#content_modul_auth_user_sec_mail").jqxInput({placeHolder: "E-Mail", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#content_modul_auth_user_sec_send_label").jqxButton({ width: 140, height: 40, theme: 'material' })
                                    .on('click', self.click_send_mail)
                    $("#content_modul_auth_user_sec_get_totp").jqxButton({ width: 140, height: 40, theme: 'material' })
                                    .on('click', self.click_totp)
                })
            } 
            $('#content_modul_auth_user_sec').show()
        },
        show: function () {
            let self = window.modul['auth_user_sec']
            window.modul['helper'].activate('auth_user_sec', self.label)
            self.set_content()
            $("#content_modul_auth_user_sec_mail").val('')
            $("#content_modul_auth_user_sec_totp").text('')
            require(['jqxinput'], function() {
                window.api_call(url='user/get_mail').then(resp => {
                    if (resp.ok) {
                        $("#content_modul_auth_user_sec_mail").val(resp.mail)
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
        },
        click_totp : function() {
           window.api_call(url='user/get_totp', {}).then(resp => {
                if (resp.ok) {
                    $("#content_modul_auth_user_sec_totp").text(resp.otp)
                } else {
                    notification.show('error', 'Fehler beim erdtellen von TOTP')
                }
            })
        }
    }
    window.modul['auth_user_sec'].init()
});