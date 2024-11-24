define('lcsmcard', ['lccore'], function() {
    (function($) {
      $.lc.addFunction('lcSmCard', init=function(ctl, options, _id){
        $(ctl).addClass('sh_card')
        $(ctl).data('type', options.type).data('panel', options.panel).data('id', options.id)
        let html = '<div class="sh_card_label">'+options.label+'</div>'
        $(ctl).append(html)
        options.keys = []
        for (const key in options.types[options.type]) {
          options.keys.push(key)
        }
        options = $.extend($.lcSmCard.defaults, options)
        let clone = Object.assign({}, options)
        $(ctl).data('lcSmCard', clone)
        postData('api', {'action': 'cards_source', 'panel': options.panel, 'card': options.id, 
                          'items': options.keys }, token=true).then(data => {
          let options = $(ctl).data('lcSmCard')
          if (data.error != null) {
            console.error(data)
          } else {
            let height = 32
            let values = {}
            let sources = {}
            for (let k=0; k<options.keys.length; k++) {
              let key = options.keys[k]
              if (options.types[options.type][key].type == 'list') {
                if (data[key] != null && data[key].value != null) {
                  height += 24
                  let html = '<div data-entry="'+key+'"'
                  if (data[key].editable) {
                    var mode = options.types[options.type][key]['editor']
                    html += ' class="sh_card_edit" data-editmode="'+mode+'"'
                  }
                  let label = options.types[options.type][key]['label']
                  if (data[key].label != undefined) {
                    label = data[key].label
                  }
                  html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">'+label+'</span>'
                  html += '<div class="sh_card_item_value"><span></span></div></div>'
                  $(ctl).append(html)
                  values[key] = data[key].value
                  sources[key] = data[key].source
                }
              } else if (options.types[options.type][key].type == 'float') {
                if (data[key] != null && data[key].value != null) {
                  height += 24
                  let html = '<div data-entry="'+key+'"'
                  if (data[key].editable) {
                    var mode = options.types[options.type][key]['editor']
                    html += ' class="sh_card_edit" data-editmode="'+mode+'"'
                  } else if (options.types[options.type][key]['history']) {
                    html += ' class="sh_card_history"'
                  }
                  let label = options.types[options.type][key]['label']
                  html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">'+label+'</span>'
                  let unit = options.types[options.type][key]['unit']
                  if (unit != '') {
                    unit = ' ' + unit
                  }                
                  html += '<div class="sh_card_item_value"><span></span>'+unit+'</div></div>'
                  $(ctl).append(html)
                  values[key] = data[key].value
                  sources[key] = data[key].source
                }
              } else if (options.types[options.type][key].type == 'color_hue') {
                requirejs(['lcrgb2hue'],function(){})
                if (data[key] != null && data[key].value != null) {
                  height += 24
                  let html = '<div data-entry="'+key+'"'
                  if (data[key].editable) {
                    var mode = options.types[options.type][key]['editor']
                    html += ' class="sh_card_edit" data-editmode="'+mode+'"'
                  }
                  let label = options.types[options.type][key]['label']
                  html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">'+label+'</span>'
                  html += '<div class="sh_card_item_value"><span><div style="height: 20px; width: 48px; border-radius: 12px;"></div></span></div></div>'
                  $(ctl).append(html)
                  let children = $(ctl).children(),
                      l = children.length
                  $(children[l-1]).data('value', {'hue':0, 'sat':0})
                  values[key] = data[key].value
                  sources[key] = data[key].source
                }
              } else if (options.types[options.type][key].type == 'color_sat') {
                if (data[key] != null && data[key].value != null) {
                  let html = '<div data-entry="'+key+'" style="height:0"'
                  html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative"></span>'
                  html += '<div class="sh_card_item_value"></div></div>'
                  $(ctl).append(html)
                  values[key] = data[key].value
                  sources[key] = data[key].source
                }
              } else if (options.types[options.type][key].type == 'date') {
                if (data[key] != null && data[key].value != null) {
                  height += 24
                  let html = '<div data-entry="'+key+'"'
                  html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">Datum</span>'
                  html += '<div class="sh_card_item_value"><span></span></div></div>'
                  $(ctl).append(html)
                  values[key] = data[key].value
                  sources[key] = data[key].source
                }
              } else if (options.types[options.type][key].type == 'weekday') {
                  if (data[key] != null && data[key].value != null) {
                    height += 24
                    let html = '<div data-entry="'+key+'"'
                    if (data[key].editable) {
                      var mode = options.types[options.type][key]['editor']
                      html += ' class="sh_card_edit" data-editmode="'+mode+'"'
                    }
                    let label = options.types[options.type][key]['label']
                    html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">'+label+'</span>'
                    html += '<div class="sh_card_item_value"><span></span></div></div>'
                    $(ctl).append(html)
                    values[key] = data[key].value
                    sources[key] = data[key].source
                  }
                } else {
                console.info(options.types[options.type][key].type)
              }
            }
            $(ctl).height(height)
            $(ctl).data('sources', sources)
            $(ctl).lcSmCard('update', values)
            var packery = $(ctl).parent().data('packery')
            if (packery != undefined) {
              packery.layout()
            }
            window.modul['page_'+options.panel].hitory_create(options.id)
            window.modul['page_'+options.panel].edit_create(options.id)
          }
        })
        // ctl is the element, options is the set of defaults + user options, _id des elements
      },
      data= {
        defaults : {
          panel: 'undefined',
          id: -1,
          label: "undefined",
          type: undefined,
          ver: 2,
          // generted
          keys : [],
          // card defitions
          types: {}
        }, 
        update : function(ctl, data) {
          let eles = $(ctl).children()
          let _options = $(ctl).data('lcSmCard')
          $(ctl).find('.sh_card_item_highlight').removeClass('sh_card_item_highlight')
          for (var i=0; i<eles.length; i++) {
            let ele = eles[i]
            let entry = $(ele).data('entry')
            if (entry != undefined) {
              let def = _options['types'][$(ctl).data('type')][entry]
              if (def.type == 'list') {
                if (data[entry] != null) {
                  let div_ele = $(ele).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      old_text = $(span_ele[0]).text(),
                      values = def.values.split('|')
                      offset = 0
                  if (def.offset != undefined) {
                    offset = def.offset
                  }    
                  new_text = values[data[entry]-offset]
                  $(ele).data('value', data[entry])
                  if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
                  $(span_ele[0]).text(new_text)
                }
              } else if (def.type == 'float') {
                if (data[entry] != null) {
                  let div_ele = $(ele).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      old_text = $(span_ele[0]).text(),
                      dec = def.decimal,
                      new_text = data[entry].toLocaleString('de-DE', {minimumFractionDigits: dec, maximumFractionDigits: dec})
                  $(ele).data('value', data[entry])
                  if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
                  $(span_ele[0]).text(new_text)
                }
              } else if (def.type == 'color_hue') {
                if (data[entry] != null) {
                  let div_ele = $(ele).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      last = $(ele).data('value')    
                  last.hue = data[entry] 
                  requirejs(['lcrgb2hue'], function(converter) {
                    span_ele.children().css('background-color', '#'+converter.hue2rgb(last.hue, last.sat, 128))
                  })       
                  $(ele).data('value', last)
                }
              } else if (def.type == 'color_sat') {
                if (data[entry] != null) {
                  let prev = $(ele).prev(),
                      div_ele = $(prev).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      last = prev.data('value')    
                  last.sat = data[entry]        
                  requirejs(['lcrgb2hue'], function(converter) {
                    span_ele.children().css('background-color', '#'+converter.hue2rgb(last.hue, last.sat, 128))
                  })       
                  prev.data('value', last)
                }
              } else if (def.type == 'date') {
                if (data[entry] != null) {
                  let div_ele = $(ele).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      old_text = $(span_ele[0]).text(),
                      sp = data[entry].split('-'),
                      new_text = sp[2]+'.'+sp[1]+'.'+sp[0]
                  $(ele).data('value', data[entry])
                  if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
                  $(span_ele[0]).text(new_text)
                }
              } else if (def.type == 'weekday') {
                if (data[entry] != null) {
                  let div_ele = $(ele).find('.sh_card_item_value'),
                      span_ele = $(div_ele[0]).find('span'),
                      old_text = $(span_ele[0]).text(),
                      sp = "unbekannt|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag".split('|'),
                      new_text = sp[data[entry]+1]
                  $(ele).data('value', data[entry])
                  if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
                  $(span_ele[0]).text(new_text)
                }
              }  
            }
          }
        },
      })
    })(jQuery)
    return $.lcSmCard
  })