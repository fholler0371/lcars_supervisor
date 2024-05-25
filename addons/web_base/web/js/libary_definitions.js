requirejs.config({
    baseUrl: '/js_lib',
    paths: {
        svginject: 'svg-inject',
        packery: 'packery',
        jqxcore: 'jqwidgets/jqxcore',
        jqxinput: 'jqwidgets/jqxinput',
        jqxpassword: 'jqwidgets/jqxpasswordinput',
        jqxbutton: 'jqwidgets/jqxbuttons',
        jqxnotification: 'jqwidgets/jqxnotification'
    },
    shim: {
        jqxinput: {deps: ["jqxcore"]},
        jqxpassword: {deps: ["jqxcore"]},
        jqxbutton: {deps: ["jqxcore"]},
        jqxnotification: {deps: ["jqxcore"]}
    }
})

add_css = function(css_file) {
    let head  = document.getElementsByTagName('head')[0]
    let link  = document.createElement('link')
    link.rel  = 'stylesheet'
    link.type = 'text/css'
    link.href = css_file
    head.appendChild(link)
}

add_css('/js_lib/jqwidgets/styles/jqx.base.css')
add_css('/css/core.css')
add_css('/css/jqx.material.css')

//cache

if ('serviceWorker' in navigator) {
    if (navigator.serviceWorker.controller == undefined) {
        navigator.serviceWorker.register('/cache.js', {scope: '/'}).then(function() {
            console.log('cache wurde aktviert')
        }).catch(function(error) {
            console.error(error)
        })
    }
}

desktop_layout = function() {
    $('body').html('<div class="header"><div class="header_l1"><div class="header_l2"><div class="header_l2i"></div></div></div></div>')
    $('.header').append('<div class="header_l3"><div class="header_l3i"></div></div>')
    $('.header').append('<div class="header_l4"></div>')
    let html = '<div class="header_content" style="color: var(--main-color_be);"><div id="header_appname"></div></div>'
    html += '<table class="header_right"><tr><td id="header_fullscreen"></td><td id="header_username"></td><td id="login_icon"></td></tr></table></div>'
    $('.header').append(html)
    $('.header').append('<div id="go_home" style="display: none"><img class="button_32" src="/img/mdi/home.svg"></div>')
    $('body').append('<div class="left"><div class="left_l1"><div class="left_l2"></div></div></div>')
    $('.left').append('<div class="left_l2"></div>')
    $('.left').append('<div class="left_l3"><div class="left_l3i"></div></div>')
    $('.left').append('<div class="main_content"></div>')

    // CREATE BUTTON UP
    $('.left_l1').append('<div class="main_button_area_up"></div>')
}

//setup core
window.api_call = function(url='', token=true, data={}, sync=false) {
    if (typeof token==='object' ) {
        data = token
        token = true
    }
    if (window.config.app_name != undefined) {
        url = '/api/' + window.config.app_name + '/' + url
    } else {
        url = '/api/' + url
    }
    if (sync) {
    } else {
        return window.api_call.async(url=url, token=token, data=data)
    }
}
window.api_call.async = function(url='', token=true, data={}) {
    var headers = {}
    if (token) {
      var token = localStorage.getItem('access_token')
      if (token != null) {
        headers = { 'Authorization': 'Bearer ' +  localStorage.getItem('access_token')}
      }
    }
    if (window.config.app_context) {
        data.context = window.config.app_context
    }
    url = location.protocol + '//' + location.host + "/" + url
    url = url.replaceAll('//', '/').replace(':/', '://')
    return fetch(url, {
        timeout: 5000,
        headers: headers,
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    }).then((response) => {
        if (response.status >= 200 && response.status <= 299) {
            return response.json();
        } else {
            return { 'error': response.status, 'text': response.text() }
        }
    }).catch(err => {
        return { 'error': 1 }
    })
}

fullscreen = {
    'activ': false,
    'init': function(){
        $('#header_fullscreen').append('<img class="button_32" src="/img/mdi/fullscreen.svg" onload="SVGInject(this)" style="top: 0">')
        $('#header_fullscreen').on('click', window.modul.fullscreen.onClick)
        $(document).on('mozfullscreenchange webkitfullscreenchange fullscreenchange', function(ev) {
            window.modul.fullscreen.activ = (document.fullscreenElement !== null)
            let img = '/img/mdi/fullscreen'
            if (window.modul.fullscreen.activ) {
                img += '-exit'
            }
            $('#header_fullscreen').html('<img class="button_32" src="'+img+'.svg" onload="SVGInject(this)" style="top: 0">')
        })
        $(document).on("keydown", function (ev) {
            if (ev.keyCode === 122) {
                window.modul.fullscreen.onClick()
                return false;
            }
        })
    },
    'onClick': function() {
        if (!window.modul.fullscreen.activ) {
            ele = document.getElementsByTagName('body')[0]
            if (ele.requestFullscreen) {
                ele.requestFullscreen()
            }   
        } else {
            if(document.exitFullscreen) {
                try {
                    document.exitFullscreen()
                } catch {}
            } 
        }
    }
}

login = {
    state : false,
    token_timer: null,
    init : function() {
        $('#login_icon').append('<img class="button_32" src="/img/mdi/login.svg" onload="SVGInject(this)" style="top: 0">')
                        .on('click', window.modul.login.onClick) 
        if (!window.modul.login.check_access_token()) {
            window.modul.login.get_access_token()          
        } else {
            window.modul.login.update_state()
        }
    },
    get_access_token: function() {
        let refresh_token = localStorage.getItem('refresh_token')
        if (refresh_token != null) {
            window.api_call(url='refresh_token', token=false, data={token: refresh_token}).then(data => {
                if (data.refresh_token == undefined) {
                    window.modul.login.do_logout()
                } else {
                    localStorage.setItem('access_token', data.access_token)
                    localStorage.setItem('refresh_token', data.refresh_token)
                    localStorage.setItem('access_token_timeout',  Math.round(new Date() / 1000 + data.expires_in))
                    window.modul.login.update_state()
                    console.log('got new token', new Date())
                }
            })
        }
    },
    update_state: function() {
        let login = window.modul.login
        let last = login.state
        if (window.modul.login.check_access_token()) {
            login.state = true
            $('#login_icon').html('<img class="button_32" src="/img/mdi/logout.svg" onload="SVGInject(this)" style="top: 0">')
            let token = localStorage.getItem('access_token').split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
            let payload = decodeURIComponent(window.atob(token).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''))
            payload = JSON.parse(payload)
            $('#header_username').text(payload.name)
            let next_check = login.left_access_token() - 60
            if (next_check < 0) {
                next_check = 1
            }
            clearTimeout(login.token_timer)
            login.token_timer = setTimeout(login.get_access_token, next_check*1000)
        } else {
            login.state = false
            $('#login_icon').html('<img class="button_32" src="/img/mdi/login.svg" onload="SVGInject(this)" style="top: 0">')
            $('#header_username').text('')
        }
        if (window.modul['manager'] != undefined) {
            if (login.state != last) {
                window.modul['manager'].update()
            }
        }
    },
    do_logout: function() {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('access_token_timeout')
        let login = window.modul.login
        clearTimeout(login.token_timer)
        login.update_state()
        window.location.replace('/')
    },
    left_access_token: function() {
        let left = -1
        let sec = new Date().getTime() / 1000
        let token_sec = localStorage.getItem('access_token_timeout')
        if (token_sec == null) {
            token_sec = 0
        }
        if (token_sec > sec) {
            left = token_sec - sec
        }
        return left
    },
    check_access_token: function() {
        if (window.modul.login.left_access_token() != -1) {
            return true
        } else {
            return false
        }
    },
    onClick : function(ev) {
        if (window.modul.login.state) {
            window.modul.login.do_logout()
        } else {
            window.api_call(url='get_login_link', token=false).then(resp => {
                if (resp.error != undefined) {
                    console.error(resp.error)
                    return
                }
                if (!resp.ok) {
                    window.modul['notification'].show('error', 'Keine Redirect URL')
                    console.error(resp.error)
                    return
                }
                let d = new Date()
                localStorage.setItem('last_redirect_state', d.getTime())
                window.location.replace(resp.redirect_url+d.getTime())
            })
        }
    }
}

helper = {
    show_home : function() {
        $('#go_home').show()
        $('#go_home').on('click', function() {
            window.location.href= '/'
        })
    },
    hide_all : function() {
        $('.content_modul').hide() 
    },
    set_label : function(label) {
        $('#header_appname').text(label)
    },
    activate : function(mod, label) {
        let self = window.modul['helper']
        self.set_label(label)
        self.hide_all()
        Object.entries(window.modul).forEach(element => {
            if (element[0] != mod && element[1].modul) {
                element[1].stop()
            }
        })
    }
}

notification = {
    init : function() {
        $('body').prepend('<div id="notifictations"><div id="notifictations_msg"></div></div>')
    },
    show : function(template, text) {
        $("#notifictations").jqxNotification({
            width: 250, position: "bottom-right", opacity: 0.8,
            autoOpen: false, animationOpenDelay: 800, autoClose: true, autoCloseDelay: 10_000, template: template
        })
        $("#notifictations_msg").text(text)
        $("#notifictations").jqxNotification('open')
    }
}

modul_clock = {
    modul: true,
    icon: '/img/mdi/clock.svg',
    label: 'Uhr',
    timer: undefined,
    stopped: false,
    already_init : false,
    init: function () {
        window.modul.helper.hide_all()
        modul.clock.already_init = true
        window.modul.clock.show()
    },
    set_content: function() {
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
    },
    show: function () {
        let self = window.modul['clock']
        self.stopped = false
        window.modul['helper'].activate('clock', self.label)
        self.set_content()
        $('#content_modul_clock').show()
        self.refresh_time()
    },
    stop: function() {
        let self = window.modul['clock']
        self.stopped = true
        if (self.timer != undefined) {
            clearTimeout(self.timer)
        }
    },
    refresh_time: function() {
        let self = window.modul['clock']
        if ($('#content_modul_clock').is(':visible')) {
            let date = new Date,
                h = date.getHours(),
                m = date.getMinutes(),
                s = date.getSeconds(),
                hp = 100 / 24 * h,
                hm = 100 / 60 * m,
                hs = 100 / 60 * s
            self.update_circle('modul_clock_seconds', hs, s)
            self.update_circle('modul_clock_minute', hm, m)
            self.update_circle('modul_clock_hour', hp, h)
            if (!self.stopped) {
                self.timer = setTimeout(self.refresh_time, 1000)
            }
            $('#modul_clock_data').text(date.toLocaleDateString('de-de', { weekday:"long", year:"numeric", month:"long", day:"numeric"}))
            date.setHours(0, 0, 0, 0)
            date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7)
            let week1 = new Date(date.getFullYear(), 0, 4)
            let week =  1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7)
            $('#modul_clock_week').text(week+'. Woche')
        }
    },
    update_circle: function(ele_name, p, v) {
        let ele = $('#'+ele_name)[0],
            ctx = ele.getContext('2d'),
            start =  1.5 * Math.PI, // Start circle from top
            end = (2 * Math.PI) / 100
        v = v < 10 ? '0' + v : v
        p = p || 100
        ele.style.width = (ele.width = 200) + "px",
        ele.style.height = (ele.height = 200) + "px"
        with (ctx) {
            lineWidth = 20
            textAlign = 'center'
            textBaseline = 'middle'
            font = '115px LCARS'
            fillStyle = '#fc9'  
            strokeStyle = '#99c'  
            clearRect(0, 0, 200, 200)
            fillText(v, 100, 100)
            beginPath()
            arc(100,100, 85, start, p * end + start, false)
            stroke()
        }
    }
}

modul_manager = {
    activ : true,
    moduls : [],
    init : function () {
        window.modul['manager'].update()
    },
    activate : function() {
        window.modul['manager'].activ = true
    },
    update : function () {
        if (window.modul['manager'].activ) {
            window.modul['manager'].activ = false
            window.modul['manager'].moduls = ['clock']
            if (!(localStorage.getItem('access_token') === null)) {
                window.api_call(url='get_allowed_moduls').then(resp => {
                    if (window.config.modul_clock == undefined || window.config.modul_clock) {
                        window.modul['manager'].moduls = [{mod: 'clock'}]
                    } else {
                        window.modul['manager'].moduls = []
                    }
                    if (resp['ok']) {
                        resp['moduls'].forEach(element => {
                            window.modul['manager'].moduls.push(element)
                        });
                    }
                    let paths = {}
                    let req_array = []
                    window.modul['manager'].moduls.forEach(element => {
                        if (window.modul[element.mod] == undefined) {
                            paths[element.mod] = element.src
                            req_array.push(element.mod)
                        }
                    })
                    requirejs.config({paths: paths })
                    if (req_array.length > 0) {
                        requirejs(req_array, function() {
                            setTimeout(window.modul['manager'].paint, 1)
                        })
                    } else {
                        setTimeout(window.modul['manager'].paint, 1)
                    }
                })
            } else {
                if (window.config.modul_clock == undefined || window.config.modul_clock) {
                    window.modul['manager'].moduls = [{mod: 'clock'}]
                } else {
                    window.modul['manager'].moduls = []
                }
                setTimeout(window.modul['manager'].paint, 1)
            }
            console.log('modul_update')
        }
        setTimeout(window.modul['manager'].activate, 1000)
    }, 
    paint : function() {
        let self = window.modul['manager']
        $('.main_button_area_up').html('')
        let i = 0
        self.moduls.forEach(element => {
            i = i + 1
            $('.main_button_area_up').height(i*60+4)
            var html = '<div class="button_left button_left_menu" data-id="'+element.mod+'" style="top: '
            html += (i-1)*60+4 + 'px ;"><img src="'+window.modul[element.mod].icon+'" class="button_32"></div>'
            $('.main_button_area_up').append(html)
        })
        $('.button_left_menu').off('click')
        $('.button_left_menu').on('click', self.click)
        if (window.modul['clock']) {
            window.modul['clock'].show()
        }
    },
    click : function(event) {
        let modul = $(this).data('id')
        window.modul[modul].show()
    }  
}

setup_core = function() {
    if (window.modul == undefined) {
        window.modul = {}
    }
    window.modul['helper'] = helper
    if (window.config.modul_clock == undefined || window.config.modul_clock) {
        window.modul['clock'] = modul_clock
        window.modul.clock.init()
    }
    window.modul['fullscreen'] = fullscreen
    fullscreen.init()
    requirejs(['jqxnotification'], function() {
        window.modul['notification'] = notification
        notification.init()
    })
    if (window.config.modul_login == undefined || window.config.modul_login) {
        window.modul['login'] = login
    } else {
        $('#header_username, #login_icon').remove()
    }
    window.modul['manager'] = modul_manager
    window.modul['manager'].init()
    window.modul.login.init()
    if (window.config.app_name && window.config.app_name != '') {
        window.modul['helper'].show_home()
    }
}