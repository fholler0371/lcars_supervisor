define([], function() {
    window.modul['withings_setup'] = {
        modul: true,
        icon: '/img/mdi/cog-outline.svg',
        label: 'Setup',
        already_init : false,
        init: function () {
        },
        set_content: function() {
            let self = window.modul['withings_setup']
            if (!($('#content_modul_withings_setup').length)) {
                var html = '<div id="content_modul_withings_setup" class="content_modul jqx-widget-content-material modul_main_base"></div>'
                $(".main_content").append(html)
                require(['jqxbutton'], function() {
                    html = '<table style="margin: 30px;"><tr><td><button id="withings_setup_button">Login</button></td></tr></table>'
                    $('#content_modul_withings_setup').append(html)
                    $('#withings_setup_button').jqxButton({theme: 'material'})
                    $('#withings_setup_button').on('click', function() {
                        window.api_call(url='setup/get_url').then(resp => {
                            if (resp.ok) {
                                window.open(resp.data.url,'_blank')
                            }
                        })
                    })
                })
            } 
            $('#content_modul_withings_setup').show()
        },
        show: function () {
            let self = window.modul['withings_setup']
            window.modul['helper'].activate('withings_setup', self.label)
            self.set_content()
        },
        stop: function() {
        
        }
    }
    window.modul['withings_setup'].init()
});