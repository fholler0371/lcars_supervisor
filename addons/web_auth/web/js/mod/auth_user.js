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
                require(['jqxinput', 'jqxbutton'], function() {
                    html = '<table style="margin: 30px;"><tr><td><input id="content_modul_auth_user_label" type="text" autocomplete="label" required/>'
                    html += '</td><td width="20px"></td><td><input type="button" value="Namen senden" id="send_label" /></td></tr>'
                    html += '<tr height="30px"></tr></table>'
                    $('#content_modul_auth_user').append(html)
                    $("#content_modul_auth_user_label").jqxInput({placeHolder: "Anzeigename", height: 30, width: 380, minLength: 5, theme: 'material' })
                    $("#send_label").jqxButton({ width: 120, height: 40, theme: 'material' })
                                    .on('click', self.click_send_label)
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
        }
    }
    window.modul['auth_user'].init()
});