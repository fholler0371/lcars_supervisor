define('lcwindow', ['lcmodal'], function() {
    (function($) {
      $.lc.addFunction('lcWindow', init=function(ctl, options, _id) {
        $(ctl).attr('tabindex', 0)
        $(ctl).css('outline', 'none').addClass('lcWindow')
        $(ctl).hide()
        $(ctl).wrap('<div id="'+_id+'_outer" style="height: 100%; width: 100%"></div>')
        $('#'+_id+'_outer').prepend('<div id="'+_id+'_modal" ></div>')
        $('#'+_id+'_modal').lcModal({occupancy: options.modal_occupancy})
        $(ctl).data('lcWindow', options)
        $(ctl).css('height', options.height).css('width', options.width).css('position', 'absolute')
        var left = ($('body').width() - $(ctl).width()) / 2
        var top = ($('body').height() - $(ctl).height()) / 2
        $(ctl).css('top', top).css('left', left)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; height: 40px; width: 8px; left: 0; top: 0; border-radius: 8px 0 0;"></div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; height: 40px; width: calc( 100% - 24px); left: 8px; top: 0">'
        html += '<span style="font-family: '+"'LCARS'"+ '; font-size: 32px; position: absolute; width: 100%; top: 6px; text-align: center;" id="'+_id+'_label"></span>'
        html += '<img src="/js/lc/close_black.png" style="position: absolute; top: 12px; right: 4px; cursor: pointer" class="close_button">'
        html += '</div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; '
        html += 'height: calc( 100% - 40px); width: 8px; left: 0; top: 40px; border-radius: 0 0 4px 4px;">'
        html += '</div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; '
        html += 'height: 8px; width: 8px; left: 8px; top: 40px"><div style="background-color: black; height: 100%; width: 100%; border-radius: 8px 0 0;"></div></div>'
        $(ctl).append(html)
        html = '<div id="'+_id+'_bar"style="background-color: '+options.frame_color+'; position: absolute; height: 40px; '
        html += 'width: calc( 100% - 24px); left: 16px; bottom: 0"></div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; height: 40px; width: 8px; right: 0; bottom: 0; border-radius: 0 0 8px;"></div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; '
        html += 'height: calc( 100% - 40px); width: 8px; right: 0; top: 0; border-radius: 4px 4px 0 0;">'
        html += '</div>'
        $(ctl).append(html)
        html = '<div style="background-color: '+options.frame_color+'; position: absolute; '
        html += 'height: 8px; width: 8px; right: 8px; bottom: 40px"><div style="background-color: black; height: 100%; width: 100%; border-radius: 0 0 8px;"></div></div>'
        $(ctl).append(html)
        html = '<div id="'+_id+'_content" style="background-color: black; position: absolute; top: 42px; left: 10px; '
        html += 'height: calc( 100% - 84px ); width: calc( 100% - 20px);"></div>'
        $(ctl).append(html)
        $(ctl).find('.close_button').on('click', function(event) {
          $($(event.currentTarget).closest('.lcWindow')).lcWindow('close')
        })
      },
      data={
        defaults: {
          modal: true,
          modal_occupancy: 0.8,
          height: '50%',
          width: '50%',
          frame_color: '#fc9'
        },
        show: function(ctl, options) {
          var _options = $(ctl).data('lcWindow')
          if (options != undefined) {
            _options = $.extend(_options, options)
            $(ctl).data('lcWindow', _options)
          }
          if (_options == undefined) {
            console.error('lcWindow not intialized')
            return
          }
          let _id = $(ctl).attr('id')
          if (_options.modal) {
            $('#'+_id+'_modal').lcModal('show', {occupancy: _options.modal_occupancy})
          }
          $(ctl).show()
          $(ctl).focus()
          $(ctl).on('keydown', function(event) {
            if (event.key == "Escape") {
              $(event.currentTarget).lcWindow('close')
            }
          })
        },
        hide: function(ctl) {
          var options = $(ctl).data('lcWindow')
          if (options == undefined) {
            console.error('lcWindow not intialized')
            return
          }
          let _id = $(ctl).attr('id')
          $('#'+_id+'_modal').lcModal('hide')
          $(ctl).hide()
        },
        close: function(ctl) {
          $.lcWindow._hide(ctl)
        },
        setTitle: function(ctl, newTitle) {
          let _id = $(ctl).attr('id')
          $('#'+_id+'_label').html(newTitle)
        }
      })
    })(jQuery)
    return $.lcWindow
  })
  