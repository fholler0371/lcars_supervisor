requirejs.config({
    baseUrl: '/js_lib',
    paths: {
        jquery: 'jquery/jquery-3.7.0',
        libary_definitions: '/js/libary_definitions'
    }
})

window.modul = {}
window.modul['login'] = {
    init : function(){
        $('#header_appname').text('Anmelden')
        if (!(localStorage.getItem('login_token') === null)) {
            let queryParams = new URLSearchParams(window.location.search)
            let data = {}
            for (const key of queryParams.keys()) data[key] = queryParams.get(key)
            data['login_token'] = localStorage.getItem('login_token')
            console.log(data)    
            window.api_call(url='do_auto_login', token=false, data=data).then(resp => {
                if (resp.error != undefined) {
                    console.error(resp.error)
                    return
                }
                console.log(resp)
                if (resp.login_token != undefined) {
                    localStorage.setItem('login_token', resp.login_token)
                }
                if (resp.redirect_url != undefined) {
                    window.location.replace(resp.redirect_url)
                }
            })
        }
        require(['jqxinput', 'jqxpassword', 'jqxbutton', 'jqxnotification'], function() {
            $('.main_content').append('<div class="loading_outer"><div class="loading_middle"><form class="loading_inner"></form></div></div>')
            $('.loading_inner').append('<input id="name" type="text" id="input" autocomplete="username" required/>')
            $("#name").jqxInput({placeHolder: "Name", height: 30, width: 380, minLength: 1, theme: 'material' })
            $('.loading_inner').append('<div style="height: 25px"></div>')
            $('.loading_inner').append('<input id="password" type="password" autocomplete="current-password" required/>')
            $("#password").jqxPasswordInput({placeHolder: "Passwort", height: 30, width: 380, minLength: 1, theme: 'material' })
            $('.loading_inner').append('<div style="height: 25px"></div>')
            $('.loading_inner').append('<input id="totp" type="text"/>')
            $("#totp").jqxInput({placeHolder: "MFA", height: 30, width: 380, minLength: 1, theme: 'material' })
            $('.loading_inner').append('<div style="height: 25px"></div>')
            $('.loading_inner').append('<input type="button" value="Anmelden" id="send" />')
            $("#send").jqxButton({ width: 120, height: 40, theme: 'material' })
                      .on('click', window.modul.login.onClick)
            $('.loading_inner').append('<input type="button" value="Passwort vergessen" id="resend" />')
            $("#resend").jqxButton({ width: 200, height: 40, theme: 'material' })
                        .on('click', window.modul.login.onNeedPassword)
                        .css('float', 'right')
        })
    },
    onNeedPassword : function(ev) {
        let queryParams = new URLSearchParams(window.location.search)
        var data = {}
        data['name'] = $("#name").val()
        console.log(data)
        window.api_call(url='reset_password', token=false, data=data).then(resp => {
            if (resp.error != undefined) {
                console.error(resp.error)
                return
            }
            window.modul.notification.show(resp.template, resp.text)
        })
        
    },
    onClick : function(ev) {
        let queryParams = new URLSearchParams(window.location.search)
        let data = {}
        for (const key of queryParams.keys()) data[key] = queryParams.get(key)
        data['name'] = $("#name").val()
        data['password'] = $("#password").val()
        data['totp'] = $("#totp").val()
        if (data['name'].length < 3) {
            notification.show('error', 'Nutzername zu kurz (3)')
            return
        }
        if (data['password'].length < 6) {
            notification.show('error', 'Passwort zu kurz (6)')
            return
        }
        window.api_call(url='do_login', token=false, data=data).then(resp => {
            if (resp.error != undefined) {
                console.error(resp.error)
                return
            }
            if (resp.login_token != undefined) {
                localStorage.setItem('login_token', resp.login_token)
            }
            if (resp.redirect_url != undefined) {
                window.location.replace(resp.redirect_url)
            }
        })
        
    }
}

requirejs(['jquery', 'libary_definitions'], function($){
    desktop_layout()
    requirejs(['svginject'], function() {
        setup_core()
    })
})