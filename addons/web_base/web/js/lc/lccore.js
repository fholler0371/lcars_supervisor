define('lccore', function() {
    (function($) {
      $.lc = {
        addFunction: function(funcName, init=undefined) {
          $.fn[funcName] = function (cmd, options, fnName=funcName) {
            if ($[fnName]['_'+cmd] != undefined) {
              this.each(function() {
                $[fnName]['_'+cmd](this, options)
              })
              return
            }
            options = cmd
            if ($[fnName]['defaults'] == undefined) {
              $[fnName]['defaults'] = {}
            }
            options = $.extend( {}, $[fnName].defaults, options );
            this.each(function() {
              new $[fnName](this,options);
            });
            return this;
          }
          $[funcName] = function(ctl, options, fnName=funcName) {
            if ($(ctl).data(fnName) != undefined) {
              console.error(fnName + ' already intialized')
              return
            }
            if ($[fnName] == undefined) {
              console.error(fnName + ' is missing')
            }
            let _id = $(ctl).attr('id')
            if (_id == undefined) {
              console.error('lcModal has no id')
            }
            $(ctl).addClass(fnName)
            if ($[funcName]['__init'] != undefined) {
              $[funcName]['__init'](ctl, options, _id)
            }
          }
          $[funcName].extend = function (obj, fnName=funcName) {
            for (let label in obj) {
              if (label == 'defaults') {
                $[funcName]['defaults'] = obj[label]
              } else {
                $[funcName]['_'+label] = obj[label]
              }
            }
          }
          $[funcName]['__init'] = init
          if (data != undefined) {
            $[funcName].extend(data)
          }
        },
        drawLcDesign : function(ele, style, thick, slim, color, background, titelId) {
          var html = '<div style="background-color: '+color+'; position: absolute; '
          if (style == 'tr' || style == 'tl') {html += 'top: 0; height: '+thick+'px; width: calc( 100% - '+slim+'px ); '}
          if (style == 'tr') {html += 'left: 0; '}
          if (style == 'tl') {html += 'right: 0; '}
          html +='text-align: center; color: '+background+'; font-size: '+thick*.75+'px" id='+titelId+'></div>'
          ele.append(html)
          html = '<div style="background-color: '+color+'; position: absolute; '
          if (style == 'tr' || style == 'tl') {html += 'top: 0; height: 100%; width: '+slim+'px; '}
          if (style == 'tr') {html += 'right: 0; border-radius: 0 '+slim+'px 0 0;'}
          if (style == 'tl') {html += 'left: 0; border-radius: '+slim+'px 0 0; '}
          html +='"><div>'
          ele.append(html)
          html = '<div style="background-color: '+color+'; position: absolute; width: '+2*slim+'px; height: '+2*slim+'px;'
          if (style == 'tr' || style == 'tl') {html += 'top: '+thick+'px; '}
          if (style == 'tr') {html += 'right: '+slim+'px; '}
          if (style == 'tl') {html += 'left: '+slim+'px; '}
          html +='"><div style="background-color: '+background+'; height: 100%; width: 100%; '
          if (style == 'tr') {html += 'border-radius: 0 '+2*slim+'px 0 0;'}
          if (style == 'tl') {html += 'border-radius: '+2*slim+'px 0 0;'}
          html += '"></div> <div>'
          ele.append(html)
        }
      }
    })(jQuery)
    return $.lc
  })