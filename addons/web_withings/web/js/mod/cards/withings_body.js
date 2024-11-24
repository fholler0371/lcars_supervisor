define(function () {
    var card = {
      create : function(panel, label, id, _) {
        var html = '<div class="sh_card" data-panel="'+panel+'" data-id="'+id+'" data-type="withings_body"><div class="sh_card_label">'+label+'</div></div>'
        $('#content_modul_page_'+panel).append(html)
        window.api_call(url='sm/cards_source', data={'panel': panel, 'card': id,
                                                     'items': ['gewicht', 'fett_anteil', 'muskeln', 'wasser', 'knochen']}).then(resp => {
          if (resp.ok) {
            var height = 32
            var values = {}
            var sources = {}
            var ele = $('#content_modul_page_'+panel).children()[id]
            if (data.gewicht != null && data.gewicht.value != null) {
              height += 24
              var html = '<div data-entry="gewicht" class="sh_card_history">'
              html += '<span class="sh_card_item_labels"  style="left: 5px; position: relative">Gewicht</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['gewicht'] = data.gewicht.value
              sources['gewicht'] = data.gewicht.source
            }
            if (data.fett_anteil != null && data.fett_anteil.value != null) {
              height += 24
              var html = '<div data-entry="fett_anteil">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Fett-Anteil</span>'
              html += '<div class="sh_card_item_value"><span></span> %</div></div>'
              $(ele).append(html)
              values['fett_anteil'] = data.fett_anteil.value
              sources['fett_anteil'] = data.fett_anteil.source
            }
            if (data.muskeln != null && data.muskeln.value != null) {
              height += 24
              var html = '<div data-entry="muskeln">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Muskeln</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['muskeln'] = data.muskeln.value
              sources['muskeln'] = data.muskeln.source
            }
            if ((data.wasser != null) && (data.wasser.value != null)) {
              height += 24
              var html = '<div data-entry="wasser">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Wasser</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['wasser'] = data.wasser.value
              sources['wasser'] = data.wasser.source
            }
            if ((data.knochen != null) && (data.knochen.value != null)) {
              height += 24
              var html = '<div data-entry="knochen">'
              html += '<span class="sh_card_item_labels" style="left: 5px; position: relative">Knochen</span>'
              html += '<div class="sh_card_item_value"><span></span> kg</div></div>'
              $(ele).append(html)
              values['knochen'] = data.knochen.value
              sources['knochen'] = data.knochen.source
            }
            $(ele).height(height)
            $(ele).data('sources', sources)
            cards.withings_body.update(panel, id, values)
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
          if (($(ele).data('entry') == 'gewicht') && (values['gewicht'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['gewicht'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'fett_anteil') && (values['fett_anteil'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['fett_anteil'].toLocaleString('de-DE', {maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'muskeln') && (values['muskeln'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['muskeln'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'wasser') && (values['wasser'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['wasser'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
          if (($(ele).data('entry') == 'knochen') && (values['knochen'] != null)) {
            var div_ele = $(ele).find('.sh_card_item_value'),
                span_ele = $(div_ele[0]).find('span'),
                old_text = $(span_ele[0]).text(),
                new_text = values['knochen'].toLocaleString('de-DE', {minimumFractionDigits: 1, maximumFractionDigits: 1})
            //if (old_text != new_text) { $(div_ele[0]).addClass('sh_card_item_highlight') }
            $(span_ele[0]).text(new_text)
          }
        }
      }
    }
    if (window.cards == undefined) { window.cards = {}}
    window.cards['withings_body'] = card
  })