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
            /*
            if (!($('#content_modul_clock').length)) {
                if ($('.loading_outer').length) { 
                    $(".main_content").html("")
                }
                let html = '<div id="content_modul_clock" class="content_modul">'
                html += '<div id="modul_clock_outer" style="height: 300px; width:600px; position: absolute; top: 50%; right: 50%; transform: translate(50%, -50%);">'
                html += '<canvas id="modul_clock_hour" style="height: 200px; width:200px; position:absolute;"></canvas>'
                html += '<canvas id="modul_clock_minute" style="height: 200px; width:200px; position:absolute; left: 200px"></canvas>'
                html += '<canvas id="modul_clock_seconds" style="height: 200px; width:200px; position:absolute; left: 400px"></canvas>'
                html += '<div id="modul_clock_data" style="color: #99c; top: 210px; position: relative; font-size: 42px; font-family: LCARS; width: 100%; text-align: center"></div>'
                html += '<div id="modul_clock_week" style="color: #99c; top: 220px; position: relative; font-size: 42px; font-family: LCARS; width: 100%; text-align: center"></div></div>'
                $(".main_content").append(html)
                
            }
            */
        },
        show: function () {
            let self = window.modul['app']
            window.modul['helper'].activate('app', self.label)
            self.set_content()
            //$('#content_modul_clock').show()
            //clock.refresh_time()
        },
        stop: function() {
        
        }
    }
    window.modul['app'].init()
});