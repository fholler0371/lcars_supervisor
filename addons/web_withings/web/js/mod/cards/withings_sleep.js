define(function () {
  var card = {
    create : function(panel, label, id, params) {
      var history = false
      let _items = ['sleep_score', 'ahi', 'bdi', 'latency', 'waso']
      if (params.length > 1 && params[1] == 'H') {
        history = true
      } 
      var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_sleep"><div class="sh_card_label">'+label+'</div></div>'
      $('#content_modul_page_'+panel).append(html)
      window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
        'items': _items}).then(resp => {
        if (resp.ok) {
          let data = resp.data
          var height = 32
          var values = {}
          var sources = {}
          var ele = $('#content_modul_page_'+panel).children()[id]
          for (let i=0; i<_items.length; i++) {
            _line_item = _items[i]
            if (data[_line_item] != null && data[_line_item].value != null) {
              if (data[_line_item].params == undefined) data[_line_item].params = {}
              height += 24
              let html = '<div data-entry="' + _line_item + '"'
              if (data[_line_item].params.hist != undefined) {
                html += ' class="sh_card_history"'
              }
              html += '><span class="sh_card_item_labels"  style="left: 5px; position: relative">' + data[_line_item].label + '</span>'
              html += '<div class="sh_card_item_value"><span></span>'
              if (data[_line_item].unit != undefined) html += ' ' + data[_line_item].unit
              html += '</div></div>'
              $(ele).append(html)
              values[_line_item] = data[_line_item].value
              sources[_line_item] = data[_line_item].source
            }
          }
          $(ele).height(height)
          $(ele).data('sources', sources)
          cards.withings_sleep.update(panel, id, values)
          var packery = $(ele).parent().data('packery')
          if (packery != undefined) {
            packery.layout()
          }
          window.modul[panel].history_create(panel, id)
        }
      })
    },
    update : function(panel, id, values) {
      var eles = $($('#content_modul_page_'+panel).children()[id]).children()
      $($('#content_modul_page_'+panel).children()[id]).find('.sh_card_item_highlight').removeClass('sh_card_item_highlight')
      for (var i=0; i<eles.length; i++) {
        var ele = eles[i]
        if (($(ele).data('entry') == 'sleep_score') && (values['sleep_score'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['sleep_score'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'ahi') && (values['ahi'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['ahi'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'bdi') && (values['bdi'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = values['bdi'].toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'latency') && (values['latency'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['latency'] / 60).toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
        if (($(ele).data('entry') == 'waso') && (values['waso'] != null)) {
          var div_ele = $(ele).find('.sh_card_item_value'),
              span_ele = $(div_ele[0]).find('span'),
              old_text = $(span_ele[0]).text(),
              new_text = (values['waso'] / 60).toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0})
          //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
          $(span_ele[0]).text(new_text)
        }
      }
    }
  }
  if (window.cards == undefined) { window.cards = {}}
  window.cards['withings_sleep'] = card
})