define([], function() {
    window.modul['router_net'] = {
        modul: true,
        icon: '/img/mdi/router-wireless.svg',
        label: 'WAN',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['router_net']
            if (!($('#content_modul_router_net').length)) {
                var html = '<div id="content_modul_router_net" class="content_modul jqx-widget-content-material modul_main_base"></div>'
                $(".main_content").append(html)
                require(['jqxinput', 'jqxbutton', 'jqxpassword'], function() {
                    html = '<table style="margin: 30px;"><tr><td>IP-V4'
                    html += '</td><td width="20px"></td><td id="content_modul_router_ipv4"></td></tr></table>'
                    $('#content_modul_router_net').append(html)
                })
            } 
            $('#content_modul_router_net').show()
        },
        show: function () {
            let self = window.modul['router_net']
            window.modul['helper'].activate('router_net', self.label)
            self.set_content()
            require(['jqxinput'], function() {
                window.api_call(url='user/get_record').then(resp => {
                    console.log(resp)
                    if (resp.ok) {
                        if (resp.data.ip4 == undefined || resp.data.ip4 == '') {
                            notification.show('info', 'Keine IP-V4 Adresse')
                        } else {
                            $('#content_modul_router_ipv4').text(resp.data.ip4)
                        }
                    } else {
                        notification.show('error', 'Router-Daten konnten nicht geladen werden')
                    }
                })
            })
        },
        stop: function() {
        
        }
    }
    window.modul['router_net'].init()
});