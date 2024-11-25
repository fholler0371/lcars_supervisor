define(function () {
    var card = {
      create : function(panel, label, id, _) {
        var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_temp"><div class="sh_card_label">'+label+'</div></div>'
        $('#content_modul_page_'+panel).append(html)
        window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
            'items': ['body_temp', 'skin_temp']}).then(resp => {
            if (resp.ok) {
            let data = resp.data
            var height = 32
            var values = {}
            var sources = {}
            var ele = $('#content_modul_page_'+panel).children()[id]
            if (data.body_temp != null && data.body_temp.value != null) {
              height += 24
              var html = '<div data-entry="body_temp" class="sh_card_history">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Körper</span>'
              html += '<div class="sh_card_item_value"><span></span> °C</div></div>'
              $(ele).append(html)
              values['body_temp'] = data.body_temp.value
              sources['body_temp'] = data.body_temp.source
            }
            if (data.skin_temp != null && data.skin_temp.value != null) {
              height += 24
              var html = '<div data-entry="skin_temp">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Haut</span>'
              html += '<div class="sh_card_item_value"><span></span> °C</div></div>'
              $(ele).append(html)
              values['skin_temp'] = data.skin_temp.value
              sources['skin_temp'] = data.skin_temp.source
            }
            $(ele).height(height)
            $(ele).data('sources', sources)
            cards.withings_temp.update(panel, id, values)
            var packery = $(ele).parent().data('packery')
            if (packery != undefined) {
              packery.layout()
            }
            window.modul['page_'+panel].hitory_create(id)
          }
        })
      },
      update : function(panel, id, values) {
        var eles = $($('#content_modul_page_'+panel).children()[id]).children()
        $($('#content_modul_page_'+panel).children()[id]).find('.sh_card_item_highlight').removeClass('sh_card_item_highlight')
        for (var i=0; i<eles.length; i++) {
          var ele = eles[i]
          if (($(ele).data('entry') == 'body_temp') && (values['body_temp'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['body_temp'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'skin_temp') && (values['skin_temp'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['skin_temp'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
        }
      }
    }
    if (window.cards == undefined) { window.cards = {}}
    window.cards['withings_temp'] = card
  })