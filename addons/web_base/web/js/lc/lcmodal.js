define('lcmodal', ['lccore'], function() {
    (function($) {
      $.lc.addFunction('lcModal', init=function(ctl, options, _id){
        // ctl is the element, options is the set of defaults + user options, _id des elements
        $(ctl).css('height', '100%').css('width', '100%').css('position', 'absolute').css('top', 0).css('left', 0)
        $(ctl).hide()
      },
      data= {
        defaults : {
          occupancy: 0.8
        }, 
        show : function(ctl, options) {
          var _options = $(ctl).data('lcModal')
          if (options != undefined) {
            _options = $.extend(_options, options)
          }
          if (_options == undefined) {
            console.error('lcModal not intialized')
            return
          }
          $(ctl).css('background', 'rgba(0, 0, 0, '+_options.occupancy+')').css('opacity', 1)
          $(ctl).show()
        },
        hide : function(ctl) {
          $(ctl).css('opacity', 0)
          $(ctl).hide()
        }
      })
    })(jQuery)
    return $.lcModal
  })