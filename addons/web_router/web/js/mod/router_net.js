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
                    html += '</td><td width="20px"></td><td id="content_modul_router_ipv4"></td></tr><tr height="15px"></tr><tr><td>Prefix</td><td></td>'
                    html += '<td id="content_modul_router_prefix"></td></tr><tr height="15px"></tr><tr><td>'
                    html += ''
                    html += '<span id="content_modul_router_link_fritz">Fritzbox</span></td><td></td>'
                    html += '<td id="content_modul_router_fritz"></td></tr></table>'
                    $('#content_modul_router_net').append(html)
                })
            } 
            $('#content_modul_router_net').show()
        },
        show: function () {
            let self = window.modul['router_net']
            window.modul['helper'].activate('router_net', self.label)
            self.set_content()
            setTimeout(window.modul['router_net'].load_link, 1000)
            require(['jqxinput'], function() {
                window.api_call(url='user/get_record').then(resp => {
                    if (resp.ok) {
                        if (resp.data.ip4 == undefined || resp.data.ip4 == '') {
                            notification.show('info', 'Keine IP-V4 Adresse')
                        } else {
                            $('#content_modul_router_ipv4').text(resp.data.ip4)
                        }
                        if (resp.data.prefix == undefined || resp.data.prefix == '') {
                            notification.show('info', 'Keine IP-V6 Prefix')
                        } else {
                            $('#content_modul_router_prefix').text(resp.data.prefix)
                        }
                        if (resp.data.ip6 == undefined || resp.data.ip6 == '') {
                            notification.show('info', 'Keine Fritzbox Adresse')
                        } else {
                            $('#content_modul_router_fritz').text(resp.data.ip6)
                        }
                    } else {
                        notification.show('error', 'Router-Daten konnten nicht geladen werden')
                    }
                })
            })
        },
        load_link: function() {
            
            if ($('#content_modul_router_link_fritz').parent()[0].nodeName != 'A') {
                window.api_call(url='user/fritzlink').then(resp => {
                    if (resp.ok) {
                        $('#content_modul_router_link_fritz').wrap('<a href="' + resp.link +
                                                                   '" target="_blank" style="color: var(--main-color_or); text-decoration: none;"></a>')
                    } else {
                        notification.show('error', 'Fritzbox-Link konnte nicht geladen werden')
                    }
                })
            }

        },
        stop: function() {
        
        }
    }
    window.modul['router_net'].init()
});