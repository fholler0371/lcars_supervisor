define('lcbuttons', ['lccore'], function() {
    (function($) {
      $.lc.addFunction('lcButtonBar', init=function(ctl, options, _id){
        $(ctl).css('height', '100%')
        for (var i=0; i<options.buttons.length; i++) {
          let div = $('<div id="'+_id+'_'+i+'"></div>')
          div.lcButtonBarEntry($.extend({}, options.buttons[i], {orientation: options.orientation, height: $(ctl).height()}))
          div.lcButtonBarEntry('add_click', options.btn_fn)
          $('#'+_id).prepend(div)
        }
        if (options.orientation == 'right') {
          $($(ctl).children()[0]).css('border-right', 'solid 4px black')
        }
        if (options.orientation == 'left') {
          $($(ctl).children()[0]).css('border-left', 'solid 4px black')
        }
      },
      data= {
        defaults: {
          orientation: 'right',
          buttons: undefined,
          btn_fn: undefined
        },
        remove : function(ctl) {
          $(ctl).removeClass('lcButtonBar')
          $(ctl).html('')
        }
      })
      $.lc.addFunction('lcButtonBarEntry', init=function(ctl, options, _id){
        for (let i=0; i<options.classes.length; i++) {
          $(ctl).addClass(options.classes[i])
        }
        $(ctl).css('float', options.orientation).css('position', 'relative').css('height', '100%')
        if (options.orientation == 'right') {
          $(ctl).css('border-left', 'solid 4px black').css('right', '4px')
        }
        if (options.orientation == 'left') {
          $(ctl).css('border-right', 'solid 4px black').css('left', '4px')
        }
        $.each(options.data,function(label,value){ 
          $(ctl).data(label, value)
        })
        if (options.text != undefined) {
          let html = '<span style="margin-'
          if (options.orientation == 'right') {
            html += 'left'
          }
          if (options.orientation == 'left') {
            html += 'right'
          }
          html += ': 8px; margin-'+options.orientation+': 8px; font-family: LCARS; font-size: 24px; position: relative;'
          html += ' top: 9px; cursor: pointer" >'+options.text+'</span>'
          $(ctl).append(html)
        }
        if (options.icon != undefined) {
          h = options.height
          let html= '<div style="height: '+h+'px; width: '+h+'px; "><img src="'+options.icon+'"></div>'
          $(ctl).append(html)
        }
      },
      data= {
        defaults: {
          orientation: 'right',
          classes: [],
          data : {},
          text: undefined
        }, 
        add_click : function(ctl, fn) {
          $(ctl).off('click')
          $(ctl).css('cursor', 'pointer')
          $(ctl).on('click', fn)
        }
      })
    })(jQuery)
    return $.lcbuttons
  })