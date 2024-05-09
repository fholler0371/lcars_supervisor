requirejs.config({
    baseUrl: '/js_lib',
    paths: {
        jquery: 'jquery/jquery-3.7.0',
        libary_definitions: '/js/libary_definitions'
    }
})

window.modul = {}

requirejs(['jquery', 'libary_definitions'], function($){
    desktop_layout()
    requirejs(['svginject'], function() {
        setup_core()
    })
})