define([], function() {
    window.modul['app'] = {
        modul: true,
        icon: '/img/mdi/menu.svg',
        label: 'Anwendungen',
        already_init : false,
        init: function () {
            window.modul.helper.hide_all()
            modul.clock.already_init = true
            window.modul.clock.show()
        },
        set_content: function() {
            if (!($('#content_modul_app').length)) {
                var html = '<div id="content_modul_app" class="content_modul jqx-widget-content-material modul_main_base"></div>'
                $(".main_content").append(html)
            }
        },
        show: function () {
            let self = window.modul['app']
            window.modul['helper'].activate('app', self.label)
            self.set_content()
            window.api_call(url='app/load_list').then(resp => {
                if (resp.ok) {
                    require(['packery', 'svginject'], function(Packery) {
                        self.set_content()
                        $('#content_modul_main_base').text("")
                        let data = resp.moduls
                        for (var i=0; i<data.length; i++) {
                            var html = '<div class="modul_main_base_item" style="width: 200px; height: 200px; border: 4px solid #36c; fill: #36c; text-align: center;'
                            html += 'border-radius: 12px; color: #36c; cursor: pointer" data-domain="'+data[i].url
                            html += '"><img src="'+data[i].icon+'" height="100px" width="100px"'
                            html += ' onload="SVGInject(this)" style="position: relative; top: 20px"><div style="position: relative; top: 20px;">'+data[i].label
                            html += '</div></div>'
                            $('#content_modul_app').append(html)
                        }        
                        new Packery( '.modul_main_base', {itemSelector: '.modul_main_base_item', gutter: 20})
                        $('.modul_main_base_item').off('click')
                        $('.modul_main_base_item').on('click', function(event) {
                            let domain = $(event.currentTarget).data('domain')
                            window.location.href = domain
                        })                
                    })
                }
            })
        },
        stop: function() {
        
        }
    }
    window.modul['app'].init()
});